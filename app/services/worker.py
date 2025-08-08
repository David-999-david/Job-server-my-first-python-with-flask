from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.extensions import db


class WorkerService():

    insert_sql = text(
        '''
    insert into workers
    (name,email,phone)
    values
    (:name, :email, :phone)
    returning *
'''
    )

    @staticmethod
    def create(data: dict) -> dict:
        try:
            with db.session.begin():
                result = db.session.execute(WorkerService.insert_sql, data)
                return result.mappings().first()
        except IntegrityError:
            raise

    @staticmethod
    def createMany(data: list[dict]) -> list[dict]:
        results = []
        try:
            with db.session.begin():
                for worker in data:
                    result = db.session.execute(
                        WorkerService.insert_sql,
                        worker
                    )
                    worker = result.mappings().first()
                    results.append(worker)
            return results
        except IntegrityError:
            raise

    job_worker_insert = text(
        '''
        insert into job_worker
        (job_id,worker_id,salary)
        values
        (:jobId, :workerId, :salary)
'''
    )

    @staticmethod
    def join_job_worker(data: dict) -> str:
        check_sql = text(
            '''
        select 1 from workers
        where id = :id
'''
        )
        try:
            with db.session.begin():
                check = db.session.execute(check_sql, {"id": data['workerId']})

                if check.first() is None:
                    raise LookupError(
                        f'Worker with id={data["workerId"]} does not found!'
                        )
                db.session.execute(
                    WorkerService.job_worker_insert, data)
                return (f'Worker with id={data["workerId"]}'
                        f'is join in Job with id={data["jobId"]}')
        except IntegrityError:
            raise
