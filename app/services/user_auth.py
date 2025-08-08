from app.extensions import db
import app.extensions as extensions
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
# from itsdangerous import SignatureExpired, BadSignature


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
        except IntegrityError:
            raise
