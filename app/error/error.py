from sqlalchemy.exc import IntegrityError, DatabaseError
from werkzeug.exceptions import HTTPException
from flask_limiter.errors import RateLimitExceeded
from marshmallow import ValidationError
from flask import jsonify, current_app
from flask_jwt_extended.exceptions import CSRFError


def register_error_handler(app):

    @app.errorhandler(RateLimitExceeded)
    def on_rateLimit(e):
        resp = jsonify({
            "error": "Too many request",
            "detail": str(e)
        })
        resp.status_code = 429
        try:
            resp.headers.extend(e.get_headers())
        except Exception:
            pass
        return resp

    @app.errorhandler(HTTPException)
    def on_http(e):
        return jsonify({
            "error": e.name,
            "detail": e.description
        }), e.code

    @app.errorhandler(ValidationError)
    def on_validate(e):
        current_app.logger.info(e.messages)
        return jsonify(
            error="Validation Error",
            detail=e.messages
        ), 422

    @app.errorhandler(DatabaseError)
    def on_database(e):
        current_app.logger.exception(e)
        return jsonify(
            error="DataBase Error"
        ), 500

    @app.errorhandler(IntegrityError)
    def on_integirty(e):
        current_app.logger.exception(e)
        return jsonify(
            error="on Conflict"
        ), 409

    @app.errorhandler(LookupError)
    def on_lookup(e):
        current_app.logger.error(e)
        return jsonify(
            error="Not Found",
            detail=str(e)
        ), 404

    @app.errorhandler(Exception)
    def on_any(e):
        current_app.logger.error(e)
        return jsonify(
            error="Internal Server Error"
        ), 500


def register_jwt_error_handler(jwt, app):

    @jwt.unauthorized_loader
    def missing_token(reason: str):
        return jsonify(error="Unthorized", detail=reason), 401

    @jwt.invalid_token_loader
    def invalid_token(reason: str):
        return jsonify(error="Invalid Token", detail=reason), 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify(
            error="Token Expired",
            token_type=jwt_payload.get("type")
        ), 401

    @jwt.needs_fresh_token_loader
    def need_refresh(jwt_header, jwt_payload):
        return jsonify(
            error="Need refresh",
        ), 401

    @app.errorhandler(CSRFError)
    def csrf_exc(e):
        return jsonify(
            error="CSRF Error",
            detail=str(e)
        ), 401
