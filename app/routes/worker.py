from flask import Blueprint, request, current_app, jsonify
from sqlalchemy.exc import IntegrityError, DatabaseError
from app.schema.bulk_requirement_schema import make_bulk_schema
from app.schema.worker import WorkerSchema, JoinJobwithWorkerSchema
from marshmallow import ValidationError
from app.services.worker import WorkerService
from app.serializers import serizliDict
from flask_jwt_extended import jwt_required

worker_bp = Blueprint('worker', __name__, url_prefix='/workers')


# @worker_bp.route('/', methods=['POST'])
# def create():
#     schema = WorkerSchema()
#     try:
#         payoad = schema.load(request.get_json() or {})
#     except ValidationError as e:
#         current_app.logger.error(e.messages)
#         return jsonify({
#             "error": e.messages
#         }), 400
#     try:
#         result = WorkerService().create(payoad)
#     except IntegrityError as e:
#         current_app.logger.error(e)
#         return jsonify({
#             "error": "Integirty Error when insert worker",
#             "detail": str(e.orig)
#         }), 400
#     except DatabaseError as e:
#         current_app.logger.error(e)
#         return jsonify({
#             "error": "Database Error when insert worker",
#             "detail": str(e.orig)
#         }), 500
#     return jsonify({
#         "error": False,
#         "success": True,
#         "data": dict(result)
#     }), 201


@worker_bp.route('', methods=['POST'])
@jwt_required()
def insertMany():
    try:
        payload = make_bulk_schema(WorkerSchema).load(request.get_json() or {})
    except ValidationError as e:
        current_app.logger.warning(e.messages)
        return jsonify({
            "error": e.messages
        }), 400
    try:
        results = WorkerService().createMany(payload['items'])
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Integrity Error when insert many workers",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database Error when insert many workers",
            "detail": str(e.orig)
        }), 500
    newWorkers = [serizliDict(dict(worker)) for worker in results]
    return jsonify({
        "error": False,
        "success": True,
        "data": newWorkers
    })


@worker_bp.route('/join', methods=['POST'])
def join_job_worker():
    schema = JoinJobwithWorkerSchema()
    try:
        payload = schema.load(request.get_json() or {})
    except ValidationError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": e.messages
        }), 400
    try:
        msg = WorkerService().join_job_worker(payload)
    except LookupError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": str(e)
        }), 400
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Integrity when join worker with job",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database when join worker with job",
            "detail": str(e.orig)
        }), 500
    return jsonify({
        "error": False,
        "success": True,
        "data": msg
    }), 201
