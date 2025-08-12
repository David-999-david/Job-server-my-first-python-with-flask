from app.extensions import db
import app.extensions as extensions
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
# from itsdangerous import SignatureExpired, BadSignature
from app.security.otp import generate_random, hash_code, utcnow, compare_otp
from datetime import timedelta, datetime, timezone
from werkzeug.exceptions import BadRequest, NotFound
from flask_jwt_extended import decode_token


class AuthService():

    register_sql = text(
        '''
    insert into users
    (name, email, phone, password_hash)
    values
    (:name, :email, :phone, :password_hash)
    returning *
'''
    )

    @staticmethod
    def register(data: dict) -> tuple[dict, str]:
        check_sql = text(
            '''select 1 from users
                where email = :email
            '''
        )
        try:
            with db.session.begin():
                check_email_exist = db.session.execute(
                    check_sql, {"email": data["email"]})
                if check_email_exist.first() is not None:
                    raise LookupError(f"{data["email"]} had already taken")
                hashed_password = generate_password_hash(
                    data["password"],
                    salt_length=16
                )
                new_user = {
                    "name": data["name"],
                    "email": data["email"],
                    "phone": data["phone"],
                    "password_hash": hashed_password
                }
                user_res = db.session.execute(
                    AuthService.register_sql,
                    new_user
                )
                user = user_res.mappings().first()
                token = extensions.seralizer.dumps(
                    {"user_id": str(user['id'])}
                    )
                return user, token
        except IntegrityError:
            raise

    verified_email_sql = text(
        '''update users
           set email_verified = true
           where id = :userId
        '''
    )

    role_sql = text(
        '''select id from roles
            where name = 'worker'
        '''
    )

    user_role_sql = text(
        '''insert into user_role
            (user_id, role_id)
            values
            (:userId,:roleId)
            on conflict (user_id,role_id) do nothing
        '''
    )

    @staticmethod
    def confirm_email(token: str):
        user = extensions.seralizer.loads(token, max_age=3600)
        userId = user.get('user_id')
        try:
            with db.session.begin():
                result = db.session.execute(
                    AuthService.verified_email_sql,
                    {"userId": userId}
                )
                if result.rowcount == 0:
                    raise LookupError(
                        f'Failed when make user with id{userId}'
                        'for email verified'
                    )
                roleId = db.session.execute(
                    AuthService.role_sql
                ).scalar()
                if roleId is None:
                    raise LookupError('Role worker is mssing not found!')
                db.session.execute(
                    AuthService.user_role_sql,
                    {"userId": userId, "roleId": roleId}
                )
        except IntegrityError:
            raise

    login_sql = text(
        '''select * from users
           where email = :email
           limit 1
        '''
    )

    @staticmethod
    def login(data: dict) -> tuple[str, str]:
        try:
            with db.session.begin():
                row = db.session.execute(
                    AuthService.login_sql,
                    {"email": data['email']}
                )
                if row is None:
                    print("[LOGIN] No user found")
                    raise LookupError(
                        "User not found!"
                    )
                user = row.mappings().first()

                print("[LOGIN] Found user:", {user["id"]})

                if user['email_verified'] == 'false':
                    print("[LOGIN] Email not verified")
                    raise LookupError(
                        "Current user email not verified!"
                    )
                print("[LOGIN] Email verified OK")

                check = check_password_hash(
                    user['password_hash'], data['password'])

                if not check:
                    print("[LOGIN] Wrong password")
                    raise LookupError(
                        "Wrong Password"
                    )
                print("[LOGIN] Password OK")

                userId = user['id']

                access = create_access_token(identity=userId)

                refresh = create_refresh_token(identity=userId)
                print("[LOGIN] Tokens created successfully")
                return access, refresh
        except IntegrityError:
            raise

    otp_sql = text(
        '''insert into otp_codes
           (user_id,hash_otp,expired_at)
           values
           (:userId,:hashedOtp,:expiredIn)
           on conflict (user_id)
           do update set
           hash_otp = excluded.hash_otp,
           expired_at = excluded.expired_at,
           used = false,
           send_at = now()
        '''
    )

    @staticmethod
    def check_email(email: str) -> tuple[str, str]:

        check_sql = text(
            '''
            select id from users
            where email = :email
            limit 1
            '''
        )

        try:
            with db.session.begin():
                row = db.session.execute(
                    check_sql,
                    {"email": email}
                )
                if row is None:
                    raise LookupError(
                        f'User with email={email} not found!'
                    )
                userId = row.mappings().first()['id']
                code = generate_random()
                hashed = hash_code(code)
                expired_in = utcnow() + timedelta(minutes=10)
                otp_need = {
                    "userId": userId,
                    "hashedOtp": hashed,
                    "expiredIn": expired_in
                }
                db.session.execute(
                    AuthService.otp_sql,
                    otp_need
                )
                return code, userId

        except IntegrityError:
            raise

    check_user = text(
        '''select id from users
           where email = :email
        '''
    )

    get_otp = text(
        '''select id,hash_otp, expired_at
           from otp_codes
           where user_id=:userId
           and used = false
           limit 1
        '''
    )

    update_otp = text(
        '''update otp_codes
           set used = true
           where id = :otpId and used=false
        '''
    )

    @staticmethod
    def verify_otp(email: str, otp: str) -> str:
        with db.session.begin():
            row = db.session.execute(
                AuthService.check_user,
                {"email": email}
            ).first()
            if row is None:
                raise NotFound("User not found")
            userId = row[0]
            otp_row = db.session.execute(
                AuthService.get_otp,
                {"userId": userId}
            ).mappings().first()
            if otp_row is None:
                raise BadRequest("Can't find otp with current user")
            databaseOtp = otp_row['hash_otp']
            expired = otp_row['expired_at']
            if expired <= datetime.now(timezone.utc):
                raise BadRequest("Otp is expired")
            check = compare_otp(otp, databaseOtp)
            if not check:
                raise BadRequest("Otp is wrong")
            res = db.session.execute(
                AuthService.update_otp,
                {"otpId": otp_row['id']}
            )
            if res.rowcount != 1:
                raise BadRequest("Failed for make current otp to used")
            claims = {"scope": "password-reset", "otp_id": otp_row['id']}
            reset_token = create_access_token(
                identity=userId,
                additional_claims=claims
                )
            return reset_token

    user_sql = text(
        '''select 1 from users
            where id = :id
        '''
    )

    change_psw_sql = text(
        '''update users
            set password_hash=:hashed
            where id=:userId
        '''
    )

    @staticmethod
    def reset_password(token: str, password: str):
        if token is None:
            raise NotFound('Reset Token is missing')
        decode = decode_token(token)
        userId = decode['sub']
        with db.session.begin():
            check = db.session.execute(
                AuthService.user_sql,
                {"id": userId}
            ).first()
            if check is None:
                raise NotFound("User not found")
            hashed_psw = generate_password_hash(password, salt_length=16)
            user_res = db.session.execute(
                AuthService.change_psw_sql,
                {
                    "hashed": hashed_psw,
                    "userId": userId
                }
            )
            if user_res.rowcount != 1:
                raise BadRequest("Failed to changed password")
