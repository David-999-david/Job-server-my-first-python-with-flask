from .extensions import db


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
        nullable=True
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
