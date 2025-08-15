from app.extensions import mail, limiter
from flask import Blueprint, request, jsonify, url_for, current_app
from flask import make_response, render_template, redirect
from flask_mail import Message
# from werkzeug.security import check_password_hash
from itsdangerous import SignatureExpired, BadSignature
from app.schema.auth import RegisterSchema, LoginSchema, EmailOnlySchema
from app.schema.auth import OtpSchema, reset_password_shcema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError
from app.services.user_auth import AuthService
from flask_jwt_extended import set_access_cookies, set_refresh_cookies
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import decode_token, get_jwt_identity
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone
from urllib.parse import urlparse


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        payload = RegisterSchema().load(request.get_json() or {})
    except ValidationError as e:
        current_app.logger.error(e.messages)
        return jsonify({
            "error": e.messages
        }), 400
    try:
        user, token = AuthService().register(payload)
    except LookupError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": str(e)
        }), 400
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Integrity Error when register",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database Error when register",
            "detail": str(e.orig)
        }), 500
    confirm_url = url_for(
            "auth.confirm_email",
            token=token,
            _external=True
            )
    message = "Email Verify Link"
    message_body = f"Please click on link {user.name} " \
                   "for verify you eamil and" \
                   f" wait for regiseter success {confirm_url}"
    sendMessage = Message(message, body=message_body,
                          recipients=[user.email])
    mail.send(sendMessage)
    return jsonify({
        "message": "Check you mail for confirm your reigster account",
        "token": token,
        "confirm_url": confirm_url
    }), 201


@auth_bp.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    try:
        AuthService().confirm_email(token)
    except SignatureExpired as e:
        current_app.logger.warning(e)
        deeplink = "htayapp://verify-failed?reason=expired"
        if urlparse(deeplink).scheme in {"htayapp", "https"}:
            return redirect(deeplink, code=302)
        return render_template("verify_failed.html", reason="Expired"), 400
    except BadSignature as e:
        current_app.logger.warning(e)
        deeplink = "htayapp://verify-failed?reason=invalid"
        if urlparse(deeplink).scheme in {"htayapp", "https"}:
            return redirect(deeplink, code=302)
        return render_template("verify_failed.html", reason="invalid"), 400
    except LookupError as e:
        current_app.logger.info(e)
        return jsonify({
            "error": str(e)
        }), 400
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Integrity when verify email",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database when verify email",
            "detail": str(e.orig)
        }), 500
    deeplink = request.args.get('redirect', "htayapp://verify-success")
    if urlparse(deeplink).scheme in {"htayapp", "https"}:
        return redirect(deeplink, code=302)
    return render_template('verify_success.html'), 200


@auth_bp.route('/web/login', methods=['POST'])
def login_web():
    try:
        payload = LoginSchema().load(request.get_json() or {})
    except ValidationError as e:
        current_app.logger.error(e.messages)
        return jsonify({
            "error": e.messages
        }), 400
    try:
        access, refresh = AuthService().login(payload)
    except LookupError as e:
        current_app.logger.info(e)
        return jsonify({
            "detail": str(e)
        }), 404
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Integrity error when login",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database error when login",
            "detail": str(e.orig)
        }), 500
    response = make_response(jsonify({"message": "Login success"}), 200)

    set_access_cookies(response, access)
    set_refresh_cookies(response, refresh)

    return response


@auth_bp.route('/mobile/login', methods=['POST'])
def login_mobile():
    try:
        payload = LoginSchema().load(request.get_json() or {})
    except ValidationError as e:
        current_app.logger.error(e.messages)
        return jsonify({
            "error": e.messages
        }), 400
    try:
        access, refresh = AuthService().login(payload)
    except LookupError as e:
        current_app.logger.info(e)
        return jsonify({
            "detail": str(e)
        }), 404
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Integrity error when login",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database error when login",
            "detail": str(e.orig)
        }), 500
    decoder = decode_token(access)

    jit = decoder['jti']
    exp = decoder['exp']
    expired_at = datetime.fromtimestamp(exp, tz=timezone.utc)

    return jsonify({
        "error": False,
        "success": True,
        "access": access,
        "message": "Successfully Login",
        "refresh": refresh,
        "jit": jit,
        "exp": exp,
        "expired_at": expired_at
    })


@auth_bp.route('/web/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=['cookies'])
def refresh_web():
    uuid = get_jwt_identity()
    access = create_access_token(identity=uuid)
    refresh = create_refresh_token(identity=uuid)
    response = make_response(jsonify({"message": "Refresh success"}), 200)
    set_access_cookies(response, access)
    set_refresh_cookies(response, refresh)
    return response


@auth_bp.route('/mobile/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=['headers'])
def refresh_mobile():
    try:
        uuid = get_jwt_identity()
    except Exception as e:
        current_app.logger.error(f'Jwt error: {str(e)}')
    access = create_access_token(identity=uuid)
    refresh = create_refresh_token(identity=uuid)

    return jsonify({
        "error": False,
        "success": True,
        "newAccess": access,
        "newRefresh": refresh
    }), 201


@auth_bp.route('/check-email', methods=['POST'])
@limiter.limit("2/minute")
def check_email():
    try:
        payload = EmailOnlySchema().load(
            request.get_json() or {}
        )
    except ValidationError as e:
        current_app.logger.error(e.messages)
        return jsonify({
            "error": e.messages
        }), 400
    try:
        code, userId = AuthService().check_email(
            payload['email']
        )
    except LookupError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": str(e)
        }), 400
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": f"Integrity error when check email for userId={userId}",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": f"Database error when check email for userId={userId}",
            "detail": str(e.orig)
        }), 500
    message = "Verify Email"
    messageBody = f"This is you OTP {code}" \
                  "Please take this otp for verify your email for reset " \
                  "password"
    html = f"""
           <html>
           <body>
           <h2>Verify Your Email</h2>
           <p>Please take this otp for verify your email for reset password</p>
           <p>This is your OTP <strong>{code}</strong>
           </body>
           </html>
"""
    sendMessage = Message(subject=message,
                          recipients=[payload['email']],
                          body=messageBody,
                          html=html
                          )
    mail.send(
        sendMessage
    )
    return jsonify({
        "message": "Please check your email for get otp"
    }), 200


@auth_bp.route('/check-otp', methods=['POST'])
def check_otp():
    payload = OtpSchema().load(request.get_json() or {})
    resetToken = AuthService().verify_otp(payload['email'], payload['otp'])
    return jsonify({
        "error": False,
        "success": True,
        "resetToken": resetToken
    })


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    payload = reset_password_shcema().load(
        request.get_json() or {}
    )
    AuthService().reset_password(payload['reset_token'],
                                 payload['new_password'])
    return jsonify({
        "error": False,
        "success": True,
        "message": "Change password successfully"
    })
