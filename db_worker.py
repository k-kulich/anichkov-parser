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
    def __init__(self, db_file: str):
        """Инициализация объекта: Worker подключается к БД и создает текущую сессию."""
        global_init(db_file)  # подключиться к переданному файлу базы данных
        self.session = create_session()  # начать текущую сессию

    def get_authors(self):
        """Получить список всех авторов постов."""
