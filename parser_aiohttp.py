"""
Реализует функции, занимающиеся парсингом сайтов (работа с HTTP/HTTPS) и отправляющие данные на
обработку.
"""
import aiohttp
import asyncio
from bs4 import BeautifulSoup, element


URL = {'bitrix': 'https://portal.anichkov.ru/extranet/'}


async def async_get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()



