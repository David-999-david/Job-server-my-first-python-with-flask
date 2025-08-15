from flask_jwt_extended import (
    verify_jwt_in_request, get_jwt_identity)
from flask import g, Blueprint, request, current_app
from app.extensions import db
from sqlalchemy import text

security_bp = Blueprint('security', __name__)

public_endpoint = {
    "auth.login",
    "auth.confirm_email",
    "auth.login_web",
    "auth.login_mobile",
    "auth.check_email",
    "auth.check_otp",
    "auth.reset_password",
    "auth.refresh_mobile"
}


def fetch_role(userId: str) -> set[str]:
    role_sql = text(
        '''select r.name
            from users u
            join user_role ur on ur.user_id = u.id
            join roles r on r.id = ur.role_id
            where u.id = :userId
        '''
    )
    with db.session.begin():
        row = db.session.execute(
            role_sql,
            {"userId": userId}
        ).scalar()
        return row


def fetch_permissions(userId: str) -> set[str]:
    perms_sql = text(
        '''select p.name
            from users u
            join user_role ur on ur.user_id = u.id
            join role_permissions rp on rp.role_id = ur.role_id
            join permissions p on p.id = rp.permission_id
            where u.id = :userId
        '''
    )
    with db.session.begin():
        row = db.session.execute(
            perms_sql,
            {"userId": userId}
        )
        return set(row.scalars().all())


@security_bp.before_app_request
def attach_identity():
    if request.endpoint in public_endpoint:
        current_app.logger.info("Public path so skip before app request")
        return
    verify_jwt_in_request(optional=True)
    userId = get_jwt_identity()
    if userId is None:
        return
    g.user_id = userId
    g.role = fetch_role(userId)
    g.perms = fetch_permissions(userId)
