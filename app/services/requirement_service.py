from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.extensions import db


class RequirementService():

    sql1 = text(
        '''
    insert into requirement
    (job_id, address_id, name)
    values
    (:jobId, :addressId, :name)
    returning *
'''
    )

    @staticmethod
    def create(data: dict) -> dict:

        need = {
            "jobId": data['jobId'],
            "addressId": data['addressId'],
            "name": data['name']
        }

        checksql = text(
            '''
    select 1 from address where id= :addressId and job_id= :jobId
'''
        )

        try:
            with db.session.begin():

                check = db.session.execute(checksql, {
                    "addressId": data['addressId'],
                    "jobId": data['jobId']})

                if check.first() is None:
                    raise LookupError(
                        f"This address={data['addressId']} "
                        f"is not with this job={data['jobId']} ")

                result = db.session.execute(RequirementService.sql1, need)

                return result.mappings().first()
        except IntegrityError:
            raise

    checksql = text(
            '''
        select 1 from address where id=:addressId and job_id=:jobId
        '''
            )

    @staticmethod
    def createMany(data_list: list[dict]) -> list[dict]:
        results = []
        try:
            with db.session.begin():
                for data in data_list:
                    check = db.session.execute(RequirementService.checksql, {
                         "addressId": data["addressId"],
                         "jobId": data['jobId']
                    })
                    if check.first() is None:
                        raise LookupError(
                            f"The address with addressId={data["addressId"]}"
                            f" is not match with JobId={data["jobId"]}"
                            )
                    need = {
                        "jobId": data['jobId'],
                        "addressId": data['addressId'],
                        'name': data['name']
                    }
                    result = db.session.execute(RequirementService.sql1, need)

                    results.append(result.mappings().first())

                return results
        except IntegrityError:
            raise

    update_sql = text(
        '''
    insert into requirement
    (id, job_id, address_id, name)
    values
    (:id, :jobId, :addressId, :name)
    on conflict (id)
    do update set
    name = coalesce(excluded.name, requirement.name),
    updated_at = now()
    returning *
'''
    )

    @staticmethod
    def update(requirementId: int, data: dict) -> dict:

        check_sql = text(
            '''
        select 1 from requirement
        where id = :requirementId
        and job_id = :jobId
        and address_id = :addressId
'''
        )

        check_need = {
            "requirementId": requirementId,
            "jobId": data["jobId"],
            "addressId": data['addressId']
        }

        update_need = {
            "id": requirementId,
            "jobId": data["jobId"],
            "addressId": data['addressId'],
            "name": data['name']
        }

        try:
            with db.session.begin():
                check_res = db.session.execute(
                    check_sql, check_need)

                if check_res.first() is None:
                    raise LookupError(
                        f'There is no requirement with id={requirementId} '
                        f'matching jobId={data["jobId"]} '
                        f'and addressId={data["addressId"]}')
                update_res = db.session.execute(
                    RequirementService.update_sql,
                    update_need
                )

                return update_res.mappings().first()
        except IntegrityError:
            raise
