from app.extensions import mail
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_mail import Message
# from werkzeug.security import check_password_hash
from itsdangerous import SignatureExpired, BadSignature
from app.schema.auth import AuthSchema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError
from app.services.user_auth import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('', methods=['POST'])
def register():
    try:
        payload = AuthSchema().load(request.get_json() or {})
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
    message_body = f"Please clik on link {user.name} " \
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
        return jsonify({
            "error": str(e.message)
        }), 400
    except BadSignature as e:
        current_app.logger.warning(e)
        return jsonify({
            "error": str(e.message)
        }), 400
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
    return jsonify({
        "error": False,
        "success": True
    }), 200
