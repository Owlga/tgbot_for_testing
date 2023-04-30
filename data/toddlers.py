import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Teacher_toddler(SqlAlchemyBase):
    __tablename__ = 'teacher_toddlers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    teacher_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("teachers.id"))
    teacher = orm.relationship('Teacher')
