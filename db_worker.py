"""
Реализует класс-менеджер, взаимодействующий с базой данных.
"""

import datetime  # запись даты и времени публикации в таблицу
from data.post import Post
from data.author import Author
from data.attachment import Attachment
from data.db_session import create_session, global_init
from my_tracebacks import AuthorError, DateError


class Worker:
    """
    Отвечает непосредственно за взаимодействие с БД.
    """
    DEF_DATE = datetime.date(year=2000, month=1, day=1)  # дата-placeholder

    def __init__(self, db_file: str):
        """Инициализация объекта: Worker подключается к БД и создает текущую сессию.
        :param db_file: строка с названием файла базы данных, работа с которым производится."""
        global_init(db_file)  # подключиться к переданному файлу базы данных
        self.session = create_session()  # начать текущую сессию

    def get_authors(self):
        """Получить список всех имен авторов постов."""
        return list(map(lambda x: x.name, self.session.query(Author).all()))

    def get_author_by(self, author_id=None, name=''):
        """Получить автора по имени или айдишнику.
        :param author_id: (необязательный) id автора в БД;
        :param name: (необязательный) имя автора поста;
        !!! ВАЖНО !!! необходимо передать хотя бы один из аргументов.
        :return : объект Author, соответствующий фильтру, либо вызывает AuthorError, говорящую об
        ошибке в имени или id автора."""
        if isinstance(author_id, int):
            try:
                return list(map(lambda x: x.name,
                                self.session.query(Author).filter(Author.id == author_id)))[0]
            except IndexError:
                raise AuthorError
        try:
            return list(map(lambda x: x.id,
                            self.session.query(Author).filter(Author.name == name)))[0]
        except IndexError:
            return self.add_author(name)

    def get_attachments(self, post_id=None):
        """Получить прикрепленные файлы и ссылки.
        :param post_id: (optional) id поста, для которого искать аттачи; если не указан,
        вернуть список всех существующих.
        :return : список всех прикрепленных к конкретному посту файлов."""
        if isinstance(post_id, int):
            return list(map(lambda x: x.link,
                            self.session.query(Attachment).filter(Attachment.post_id == post_id)))
        return list(map(lambda x: x.link, self.session.query(Attachment).all()))

    def get_post_by_id(self, post_id=None):
        """Получить текст одного-единственного поста, который нас интересует.
        :param post_id: id поста (логично).
        :return: текст поста."""
        if post_id is None:
            return ''
        return list(map(lambda x: x.text,
                        self.session.query(Post).filter(Post.id == post_id)))[0]

    def get_posts(self, author_id=None, date=DEF_DATE):
        """Получить список постов. Есть возможность отфильтровать по автору или дате.
        :param author_id: id автора, по которому ищем;
        :param date: дата, за которую ищем посты;
        :return : список всех постов данного автора; если id автора указан неверно,
        функция вернет исключение AuthorError."""
        if date > self.DEF_DATE:
            return list(map(lambda x: (x.id, x.text,
                                       datetime.date.strftime(x.date, '%d.%m.%y'),
                                       self.get_author_by(x.author_id)),
                            self.session.query(Post).filter(Post.date == date)))
        if isinstance(author_id, int) and date > self.DEF_DATE:
            author = self.get_author_by(author_id)
            return list(map(lambda x: (x.id, x.text,
                                       datetime.date.strftime(x.date, '%d.%m.%y'),
                                       author),
                            self.session.query(Post).filter(Post.author_id == author_id,
                                                            Post.date == date)))
        if isinstance(author_id, int):
            author = self.get_author_by(author_id)
            return list(map(lambda x: (x.id, x.text,
                                       datetime.date.strftime(x.date, '%d.%m.%y'),
                                       author),
                            self.session.query(Post).filter(Post.author_id == author_id)))
        return list(map(lambda x: (x.id, x.text,
                                   datetime.date.strftime(x.date, '%d.%m.%y'),
                                   self.get_author_by(x.author_id)),
                        self.session.query(Post).all()))

    def add_author(self, name: str):
        """Добавить в таблицу нового автора.
        :param name: имя автора."""
        new_author = Author()
        new_author.name = name
        self.session.add(new_author)
        self.session.commit()
        return new_author.id

    def add_attachments(self, post_id: int, attachments: list):
        """Добавить в таблицу список со всеми новыми прикрепленными файлами.
        :param post_id: id поста из таблицы, к которому прикреплены все аттачи;
        :param attachments: список всех ссылок на прикрепленные файлы."""
        try:
            attaches = self.get_attachments(post_id)
        except IndexError:
            attaches = []
        for attach in attachments:
            if attach and attach in attaches:
                continue
            new_attach = Attachment()
            new_attach.link = attach
            new_attach.post_id = post_id
            self.session.add(new_attach)
        self.session.commit()

    def add_post(self, author: str, text: str, attaches: list, date=DEF_DATE):
        """Добавить в таблицу пост со всей информацией о нем.
        :param author: имя автора поста;
        :param text: текст самого сообщения;
        :param attaches: список всех прикрепленных к посту файлов;
        :param date: дата публикации поста."""
        au = self.get_author_by(name=author)
        try:
            is_in = text in map(lambda x: x[1], self.get_posts(author_id=au))
        except IndexError:
            is_in = False
        if is_in:
            return
        post = Post()
        post.author_id = au
        post.text = text
        post.date = date
        self.session.add(post)
        self.session.commit()
        self.add_attachments(post.id, attaches)

    def close_session(self):
        """Закрыть сессию (использовать метод перед завершением работы приложения)."""
        self.session.commit()
        self.session.close()
