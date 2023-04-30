import sqlalchemy
from .db_session import SqlAlchemyBase

from sqlalchemy import orm


class Teacher(SqlAlchemyBase):
    __tablename__ = 'teachers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    toddlers = orm.relationship("Teacher_toddler", back_populates='teacher')
    tests = orm.relationship("Teacher_test", back_populates='teacher')
