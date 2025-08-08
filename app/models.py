from .extensions import db
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True),
                   primary_key=True,
                   server_default=sa.text('gen_random_uuid()')
                   )
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.Text, nullable=True)
    password_hash = db.Column(db.Text, nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
        )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    called_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    addresses = db.relationship(
        'Address', back_populates='job',
        cascade='all, delete-orphan'
        )

    requirements = db.relationship(
        'Requirement', back_populates='job',
        cascade='all, delete-orphan'
    )

    workers = db.relationship(
        'Worker',
        secondary='job_worker',
        back_populates='job',
    )


class Address(db.Model):
    __tablename__ = 'address'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(
        db.Integer, db.ForeignKey('job.id', ondelete='cascade'),
        nullable=False)
    street = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(200), nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
        )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    salaries = db.relationship(
        'Salary', back_populates='address',
        cascade='all, delete-orphan'
        )

    requirements = db.relationship(
        'Requirement', back_populates='address',
        cascade='all, delete-orphan'
    )

    job = db.relationship(
        'Job', back_populates='addresses'
    )


class Salary(db.Model):
    __tablename__ = 'salary'

    id = db.Column(db.Integer, primary_key=True)
    address_id = db.Column(
        db.Integer, db.ForeignKey('address.id', ondelete='cascade'),
        nullable=False
        )
    amount = db.Column(
        db.Numeric(12, 2), nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    address = db.relationship(
        'Address', back_populates='salaries'
    )


class Requirement(db.Model):
    __tablename__ = 'requirement'

    id = db.Column(
        db.Integer, primary_key=True
    )
    job_id = db.Column(
        db.Integer,
        db.ForeignKey('job.id', ondelete='cascade'),
        nullable=False
    )
    address_id = db.Column(
        db.Integer,
        db.ForeignKey('address.id', ondelete='cascade'),
        nullable=False
    )
    name = db.Column(
        db.Text,
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    job = db.relationship('Job', back_populates='requirements')

    address = db.relationship(
        'Address', back_populates='requirements'
    )


class Worker(db.Model):
    __tablename__ = 'workers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(30), nullable=False)
    hired_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    fired_at = db.Column(
        db.DateTime,
        nullable=True
    )

    job = db.relationship(
        'Job',
        secondary='job_worker',
        back_populates='workers'
    )

    job_worker = db.relationship(
        'Job_Worker',
        back_populates='workers',
        cascade='all, delete-orphan'
    )


class Job_Worker(db.Model):
    __tablename__ = 'job_worker'

    job_id = db.Column(
        db.Integer,
        db.ForeignKey('job.id', ondelete='cascade'),
        nullable=False
    )
    worker_id = db.Column(
        db.Integer,
        db.ForeignKey('workers.id', ondelete='cascade'),
        nullable=False
    )
    salary = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )
    assigned_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    job = db.relationship(
        'Job',
        back_populates='job_worker'
    )

    workers = db.relationship(
        'Worker',
        back_populates='job_worker'
    )
