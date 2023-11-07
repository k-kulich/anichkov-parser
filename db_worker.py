"""
Реализует класс-менеджер, взаимодействующий с базой данных.
"""

import datetime  # запись даты и времени публикации в таблицу
from data.post import Post
from data.author import Author
from data.attachment import Attachment
from data.db_session import create_session, global_init


class Worker:
    """
    Отвечает непосредственно за взаимодействие с БД.
    """
    DEF_DATE = datetime.date(year=2000, month=1, day=1)  # дата-placeholder

    def __init__(self, db_file: str):
        """Инициализация объекта: Worker подключается к БД и создает текущую сессию."""
        global_init(db_file)  # подключиться к переданному файлу базы данных
        self.session = create_session()  # начать текущую сессию

    def get_authors(self):
        """Получить список всех имен авторов постов."""
        return list(map(lambda x: x.name, self.session.query(Author).all()))

    def get_author_by(self, author_id=0, name=''):
        """Получить автора по имени или айдишнику."""
        if author_id:
            return list(map(lambda x: x.name,
                            self.session.query(Author).filter(Author.id == author_id)))[0]
        return list(map(lambda x: x.id, self.session.query(Author).filter(Author.name == name)))[0]

    def get_attachments(self, post_id=0):
        """Получить прикрепленные файлы и ссылки.
        Опциональный параметр post_id - id поста, для которого искать аттачи; если не указан,
        вернуть список всех существующих."""
        if post_id:
            return list(map(lambda x: x.link,
                            self.session.query(Attachment).filter(Attachment.post_id == post_id)))
        return list(map(lambda x: x.link, self.session.query(Attachment).all()))

    def get_posts(self, author_id=0, date=datetime.date(year=2000, month=1, day=1)):
        """Получить список постов. Есть возможность отфильтровать по автору или дате."""
        if author_id and date > self.DEF_DATE:
            author = self.get_author_by(author_id)
            return list(map(lambda x: (x.text, x.date, author),
                            self.session.query(Post).filter(Post.author_id == author_id,
                                                            Post.date == date)))
        if author_id:
            author = self.get_author_by(author_id)
            return list(map(lambda x: (x.text, x.date, author),
                            self.session.query(Post).filter(Post.author_id == author_id)))
        return list(map(lambda x: (x.text, x.date, self.get_author_by(x.author_id)),
                        self.session.query(Post).all()))
