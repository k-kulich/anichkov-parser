"""Сравнение скоростей работы библиотек."""
import time  # модуль, необходимый для фиксации времени
import requests
import aiohttp
import asyncio  # модуль, позволяющий работать асинхронно в питоне


URL = "http://httpbin.org/delay/1"  # адрес сайта, имитирующего работу реальных сайтов с задержками
TRIES = 10  # число тестовых запросов к сайту
loop = asyncio.get_event_loop()
req, aio = [], []


async def async_get(url):  # асинхронно могут выполняться только функции
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await response.read()


for i in range(TRIES):
    start = time.time()
    for j in range(TRIES):
        requests.get(URL)  # отправляем GET-запрос через requests
    res = float(time.time() - start)
    print(f'{i + 1}) Time for requests:\t\t{res}')
    req.append(res)

    start = time.time()  # обновляем таймер
    # запускаем асинхронно функцию
    loop.run_until_complete(asyncio.gather(*[async_get(URL) for k in range(TRIES)]))
    res = float(time.time() - start)
    print(f'{i + 1}) Time for aiohttp:\t\t{res}\n')
    aio.append(res)


print('-' * 90)
print(f'\nAverage\t\tRequests:\t{sum(req) / TRIES}\t\taiohttp:\t{sum(aio) / TRIES}\n')
print('-' * 90)
