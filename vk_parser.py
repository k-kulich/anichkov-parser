"""
Реализует класс, занимающийся парсингом сайтов (работа с HTTP/HTTPS/API) и отправляющий данные на
обработку.
"""
import datetime  # для преобразования из unixtime в человеческий
import os  # для получения переменной окружения
from vk_api import VkApi, exceptions  # готовая библиотека для работы с VK API
from my_tracebacks import NoTokenError  # ошибка токена доступа


class Parser:
    """
    Объект, осуществляющий поиск информации на сайтах и возвращающий ее для дальнейшей обработки.
    Использует BeautifulSoup для удобного просмотра HTML-кода страниц.
    """
    URL = {'bitrix': 'https://portal.anichkov.ru/extranet/'}
    VK_GROUPS = {'198282852': 'обществознание', '198221930': 'организационный',
                 '186147026': 'история', '207108934': 'словесность 11Б', '199474162': 'физика',
                 '186426728': 'олимпиадное движение АЛ', '222581416': 'microAL',
                 '186822601': 'ШСК Аничков'}

    def __init__(self):
        token = os.getenv("VK_TOKEN")
        if not token:
            raise NoTokenError
        try:
            self.vk_session = VkApi(token=token)
        except exceptions.ApiError:
            raise NoTokenError
        self.vk = self.vk_session.get_api()

    @staticmethod
    def __save_vk_attaches(attachments: list, message: tuple):
        """
        Получить только нужную инфу о закрепах и сохоранить ее в посте.
        :param attachments: список аттачей записи, возвращаемых из vk через json (vk_api конвертит).
        :param message: пост, в котором будет сохранена ссылка на аттач.
        :return: None.
        """
        for attach in attachments:  # перебираем все прикрепленные вещи
            tp = attach['type']  # тип файла
            if tp not in ('photo', 'doc', 'link'):  # нам нужны только 3 типа аттачей
                continue
            size, url = 'unknown', ''
            if tp in {'doc', 'link'}:
                title = attach[tp]['title']
                url = attach[tp]['url']
            else:
                title = 'photo'
                for sz in attach[tp]['sizes']:
                    if sz['type'] == 'y':
                        url = sz['url']
                        break
            message += ((url, title, size, tp),)  # добавить к сообщению
        return message

    def parse_vk(self, post_count=3):
        """
        Вытянуть информацию из сообществ в вк через API.
        :param post_count: число последних постов, откуда брать данные. Из каждого сообщества
        возьмется такое количество постов.
        :return: список объектов post.Post, хранящих в себе всю нужную информацию и ссылки.
        """
        posts = []
        for group in self.VK_GROUPS:  # перебрать сообщества
            try:
                response = self.vk.wall.get(owner_id='-' + group, count=post_count)
            except exceptions.ApiError:
                raise NoTokenError
            # перебрать посты в сообществе
            for item in response['items']:
                subj = self.VK_GROUPS[group]  # предмет, задание по которому опубликовано
                # возвращает мне время в UNIXTIME, так что преобразовываем в человеческий
                tm = datetime.datetime.utcfromtimestamp(item['date'])
                date = datetime.date(year=tm.year, month=tm.month, day=tm.day)
                message = ((subj, date),)  # всю информацию о посте храним в кортеже
                message += (item['text'].replace('\\n', '\n'),)  # сохранить текст поста
                if item.get('attachments', False):  # если есть, то распарсить аттачи
                    message = self.__save_vk_attaches(item['attachments'], message)
                posts.append(message)
        return posts
