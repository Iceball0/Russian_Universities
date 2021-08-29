import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Reviews(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'reviews'

    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True,
                           primary_key=True, autoincrement=True)
    user_name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    user_email = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    university_id = sqlalchemy.Column(sqlalchemy.Integer,
                                      sqlalchemy.ForeignKey("universities.id"))
    universities = orm.relation('Universities')

    def __repr__(self):
        return f'<Reviews> {self.id} {self.user_name} {self.text} {self.rating}'