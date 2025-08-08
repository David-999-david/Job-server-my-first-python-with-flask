from flask import request, Blueprint, current_app, jsonify
from sqlalchemy.exc import IntegrityError, DatabaseError
from app.schema.bulk_requirement_schema import make_bulk_schema
from marshmallow import ValidationError
from app.services.requirement_service import RequirementService
from app.serializers import serizliDict
from app.schema.requirement import RequirementSchema

requirement_bp = Blueprint('requirement', __name__, url_prefix='/requirements')

# @requirement_bp.route('', methods=['POST'])
# def create():
#     schema = RequirementSchema()
#     try:
#         payload = schema.load(request.get_json() or {})
#     except ValidationError as e:
#         current_app.logger.error(e.messages)
#         return jsonify({
#             "error": e.messages
#         })
#     try:
#         result = RequirementService().create(payload)
#     except LookupError as e:
#         current_app.logger.error(e)
#         return jsonify({
#             "detail": e
#         })
#     except IntegrityError as e:
#         current_app.logger.error(e)
#         return jsonify({
#             "error": "Integrity when create requirement",
#             "detail": str(e.orig)
#         })
#     except DatabaseError as e:
#         current_app.logger.error(e)
#         return jsonify({
#             "error": "Database Error when create requirement",
#             "detail": str(e.orig)
#         })
#     requirement = serizliDict(dict(result))

#     return jsonify({
#         "error": False,
#         "success": True,
#         "data": requirement
#     })


@requirement_bp.route('', methods=['POST'])
def createMany():

    try:
        payload = make_bulk_schema(RequirementSchema).load(
            request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({
            "error": True,
            "detail": str(e.messages)
        }), 400
    try:
        results = RequirementService().createMany(payload['items'])
    except LookupError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": str(e)
        }), 400
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Integrity when added many requirement",
            "detial": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database error when added many requirements",
            "detail": str(e.orig)
        }), 500
    requirements = []

    for item in results:
        requirements.append(serizliDict(dict(item)))
    return jsonify({
        "error": False,
        "success": True,
        "data": requirements
    }), 201


@requirement_bp.route('/<int:id>', methods=["PUT"])
def update(id):
    scheme = RequirementSchema()

    try:
        payload = scheme.load(request.get_json() or {})
    except ValidationError as e:
        current_app.logger.error(e.messages)
        return jsonify({
            "error": str(e)
        }), 400
    try:
        result = RequirementService().update(
            requirementId=id, data=payload)
    except LookupError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Lookup Error when update requirement",
            "detail": str(e)
        })
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Intergity Error when update requirement",
            "detail": str(e.orig)
        })
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database Error when update requirement",
            "detail": str(e.orig)
        })
    new_require = serizliDict(dict(result))
    return jsonify({
        "error": False,
        "success": True,
        "data": new_require
    })


@requirement_bp.route('', methods=['DELETE'])
def delete_many():
    data = request.get_json() or {}
    ids = data.get('ids')

    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({
            "error": "The ids is not valid of list"
        }), 400
    try:
        result = RequirementService().deleteMany(ids=ids)
    except LookupError as e:
        current_app.logger.error(str(e))
        return jsonify({
            "error": str(e)
        })
    except IntegrityError as e:
        current_app.logger.error(str(e))
        return jsonify({
            "error": "Integrity error when delete many requirements",
            "detail": str(e.orig)
        })
    except DatabaseError as e:
        current_app.logger.error(str(e))
        return jsonify({
            "error": "DateBase error when delete many requirements",
            "detail": str(e.orig)
        })
    return jsonify({
        "error": False,
        "success": True,
        "deleteCount": result
    }), 200
