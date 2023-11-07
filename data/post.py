import sqlalchemy
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    """Создание таблицы постов ('posts')."""
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('authors.id'))
    date = sqlalchemy.Column(sqlalchemy.Date)  # дата публикации
    text = sqlalchemy.Column(sqlalchemy.String)
