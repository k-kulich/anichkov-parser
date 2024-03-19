class AuthorError(Exception):
    def __init__(self):
        self.txt = 'Ошибка в имени автора.'


class DateError(Exception):
    def __init__(self):
        self.txt = 'Ошибка даты.'


class NoTokenError(Exception):
    def __init__(self):
        self.txt = 'Ошибка: токен доступа отсутствует или недействителен.'


class NeedSave(Exception):
    """По сути вообще не исключение, я для удобства его использую."""
