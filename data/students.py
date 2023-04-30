import sqlalchemy
from .db_session import SqlAlchemyBase


class Student(SqlAlchemyBase):
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    points = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    test = sqlalchemy.Column(sqlalchemy.String, nullable=True)
