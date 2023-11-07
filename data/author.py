import sqlalchemy
from .db_session import SqlAlchemyBase


class Author(SqlAlchemyBase):
    """Создание таблицы авторов постов ('authors')."""
    __tablename__ = "authors"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
