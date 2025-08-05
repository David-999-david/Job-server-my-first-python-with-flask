from app.extensions import db
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


class AddressSalaryService():

    _addressSql = text(
        '''
    insert into address
    (job_id,street,city,country)
    values
    (:jobId, :street, :city, :country)
    returning *
'''
    )

    _salarySql = text(
        '''
    insert into salary
    (address_id, amount)
    values
    (:addressId, :amount)
    returning *
'''
    )

    @staticmethod
    def create(data: dict) -> tuple[dict, dict]:
        try:
            with db.session.begin():

                insertAddress = db.session.execute(
                    AddressSalaryService._addressSql,
                    {
                        "jobId": data['jobId'],
                        "street": data['street'],
                        "city": data['city'],
                        "country": data['country']
                    }
                    )
                addressrow = insertAddress.mappings().first()
                addressId = addressrow["id"]

                insertSalary = db.session.execute(
                    AddressSalaryService._salarySql,
                    {
                        "addressId": addressId,
                        "amount": data['amount']
                    }
                )
                salaryrow = insertSalary.mappings().first()

                return addressrow, salaryrow
        except IntegrityError:
            raise

    _link_one_sql = text(
        '''
    select
    j.id as "jobId",
    j.name as "jobName",
    j.called_at as "calledAt",
    coalesce(
    jsonb_agg(
    jsonb_build_object(
    'addressId', a.id,
    'street', a.street,
    'city', a.city,
    'country', a.country,
    'amount', s.amount
    )
    ) filter (where a.id is not null),
    '[]'
    ) as links
    from job as j
    left join address as a on a.job_id = j.id
    left join salary as s on s.address_id = a.id
    where j.id = :jobId
    group by j.id, j.name, j.called_at;
'''
    )

    _link_all_sql = text(
        '''
    select
    j.id as "jobId",
    j.name as "jobName",
    j.called_at as "calledAt",
    coalesce(
    jsonb_agg(
    jsonb_build_object(
    'addressId', a.id,
    'street', a.street,
    'city', a.city,
    'country', a.country,
    'amount', s.amount
    )
    ) filter (where a.id is not null),
    '[]'
    ) as links
    from job as j
    left join address as a on a.job_id = j.id
    left join salary as s on s.address_id = a.id
    group by j.id, j.name, j.called_at;
'''
    )

    _link_search_sql = text(
        '''
    select
    j.id as "jobId",
    j.name as "jobName",
    j.called_at as "calledAt",
    coalesce(
    jsonb_agg(
    jsonb_build_object(
    'addressId', a.id,
    'street', a.street,
    'city', a.city,
    'country', a.country,
    'amount', s.amount
    )
    ) filter (where a.id is not null),
    '[]'
    ) as links
    from job as j
    left join address as a on a.job_id = j.id
    left join salary as s on s.address_id = a.id
    where j.name ilike :query
    or a.street ilike :query
    or a.city ilike :query
    or a.country ilike :query
    or cast(s.amount as text) ilike :query
    group by j.id, j.name, j.called_at;
'''
    )

    @staticmethod
    def getAll() -> list[dict]:

        try:
            with db.session.begin():
                link_rows = db.session.execute(
                    AddressSalaryService._link_all_sql)

                return link_rows.mappings().fetchall()
        except IntegrityError:
            raise

    @staticmethod
    def getById(jobId: int) -> dict:
        try:
            with db.session.begin():
                rows = db.session.execute(
                    AddressSalaryService._link_one_sql,
                    {"jobId": jobId})

                return rows.mappings().first()
        except IntegrityError:
            raise

    @staticmethod
    def search(query: str) -> list[dict]:
        try:
            with db.session.begin():
                rows = db.session.execute(
                    AddressSalaryService._link_search_sql,
                    {"query": f"%{query}%"})
                return rows.mappings().fetchall()
        except IntegrityError:
            raise

    _edit_addr = text(
        '''
    insert into address
    (id,job_id,street,city,country)
    values
    (:id,:jobId,:street,:city,:country)
    on conflict (id)
    do update
    set
    job_id= coalesce(excluded.job_id, address.job_id),
    street= coalesce(excluded.street, address.street),
    city= coalesce(excluded.city, address.city),
    country= coalesce(excluded.country, address.country),
    updated_at = now()
'''
    )

    _edit_salary = text(
        '''
    insert into salary
    (id,address_id,amount)
    values
    (:id,:addressId,:amount)
    on conflict (id)
    do update set
    address_id = coalesce(excluded.address_id, salary.address_id),
    amount = coalesce(excluded.amount, salary.amount),
    updated_at = now()
'''
    )


@staticmethod
def update(addressId: int, salaryId: int, data: dict) -> tuple[dict, dict]:
    try:
        with db.session.begin():
            add_res = db.session.execute(
                AddressSalaryService._edit_addr,
                {
                    "id": addressId,
                    "jobId": data['jobId'],
                    "street": data['street'],
                    "city": data['city'],
                    "country": data['country']
                 }
                )
            upd_add = add_res.mappings().first()

            sala_res = db.session.execute(
                AddressSalaryService._edit_salary,
                {
                    "id": salaryId,
                    "addressId": addressId,
                    "amount": data['amount']
                }
            )
            upd_sal = sala_res.mappings().first()

            return upd_add, upd_sal
    except IntegrityError:
        raise
