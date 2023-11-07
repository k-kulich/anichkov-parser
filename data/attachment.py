import sqlalchemy
from .db_session import SqlAlchemyBase


class Attachment(SqlAlchemyBase):
    """Создание таблицы ссылок на прикрепленные файлы ('attachments')."""
    __tablename__ = "attachments"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))
    link = sqlalchemy.Column(sqlalchemy.String)
