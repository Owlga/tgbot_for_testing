import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Teacher_test(SqlAlchemyBase):
    __tablename__ = 'teacher_tests'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    teacher_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("teachers.id"))
    teacher = orm.relationship('Teacher')
