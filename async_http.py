"""
Реализует функции, занимающиеся парсингом сайтов (работа с HTTP/HTTPS) и отправляющие данные на
обработку.
"""
import os
import aiohttp
from bs4 import BeautifulSoup, element
from my_tracebacks import NoTokenError
from correct_data import rewrite_format


URL = {'bitrix': 'https://portal.anichkov.ru/extranet/'}
login, password = os.getenv('BX_LOGIN'), os.getenv('BX_PASSWORD')
if not all((login, password)):
    raise NoTokenError
BITRIX_AUTH = aiohttp.BasicAuth(login, password=password)


async def async_get(url, auth=None):
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get(url) as response:
            return await response.text(), response.content


async def get_bitrix_soup():
    html_code = await async_get(URL['bitrix'], BITRIX_AUTH)
    return BeautifulSoup(html_code[0], 'lxml')


async def save_bitrix_links(tag, message: tuple):
    """
    Сохранить всю информацию о файлах - ссылку на скачивание, название, размер - в Post.
    :param tag: тег, в котором находятся все аттачи конкретного сообщения.
    :param message: tuple, в конец которого необходимо записать ссылки.
    :return: message (updated).
    """
    for div in tag.contents[1].contents[3].children:
        # в данном случае вместо обработки исключения проще избежать его возбуждения
        if type(div) == element.NavigableString:
            continue
        a = div.contents[3].a
        # запомнить все данные по файлам
        message += ((a['href'], a['data-title'], 'doc'),)
    return message


async def parse_bitrix(post_limit=8):
    """
    Вытянуть информацию с портала Аничкова, сделанного в рамках Bitrix24.
    :param post_limit: int, обозначает число последних записей, с которых нужно взять данные. По
    умолчанию просматриваются последние 8 записей.
    :return: list[tuple[str]], список, в котором каждый пост представлен кортежем из двух других
    кортежей: "шапка" (имя публикующего и дата публикации) и "тело" (текст сообщения и список
    названий файлов). Если пользователь ввел post_limit < 1, то вернуть пустой список.
    """
    if post_limit < 1:
        return []
    soup = await get_bitrix_soup()  # получить удобный для парсинга HTML-код страницы
    posts = []  # список постов

    for tag in soup.find_all('div', class_='feed-post-title-block', limit=post_limit):
        # получить данные из "шапки" поста
        post_head = str(tag.contents[0].get_text()), str(tag.contents[2].contents[0].get_text())
        date = post_head[1]
        if len(date.split()) == 2:
            message = ((post_head[0], rewrite_format(date, has_month=False)),)
        elif len(date.split()) == 3:
            message = ((post_head[0], rewrite_format(date)),)
        else:
            message = ((post_head[0], rewrite_format(date, year_given=True)),)
        if post_head[0] == 'portal.anichkov.ru':
            message += ('Добавлен новый внешний пользователь',)

        # получить текст сообщения
        for string in tag.next_sibling.contents[0].stripped_strings:
            message += (str(string).replace('\xa0', ''),)

        # перейти к тегу, который должен содержать аттачи
        nxt = tag.next_sibling.next_sibling
        while str(nxt.name) != 'div':
            nxt = nxt.next_sibling
        # если аттачи у текущего сообщения вообще имеются
        if 'disk-attach-block' in str(nxt.get('id')):
            # добавить список названий аттачей к тексту поста
            message = await save_bitrix_links(nxt, message)
        posts.append(message)

    return posts


async def save_attaches(url_list: list, dirpath: str):
    """
    Записать данные из файла по ссылке в файл с указанным путем.
    :param url_list: адрес ресурса, с которого берем файл. [(имя файла, путь), ...]
    :param dirpath: путь к файлу на компьютере пользователя, куда надо его записать.
    :return: None.
    """
    for url in url_list:
        resp = await async_get(url[1])
        async with open(dirpath + '\\' + url[0], mode='wb') as infile:
            infile.write(resp[1])

