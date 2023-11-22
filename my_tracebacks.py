class AuthorError(Exception):
    def __init__(self):
        self.txt = 'Ошибка в имени автора.'


class DateError(Exception):
    def __init__(self):
        self.txt = 'Ошибка даты.'
