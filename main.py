import sys
import asyncio
import async_http as ahttp
import vk_parser as pp
import db_worker
from gui import MyGUI
from PyQt5.QtWidgets import QApplication
from my_tracebacks import NoTokenError


async def main():
    my_worker = db_worker.Worker('db\\test-0-1.db')
    # попытка инициализировать парсер, в случае ошибки завершение программы
    try:
        parser = pp.Parser()
    except NoTokenError as e:
        print(e.txt, file=sys.stderr)
        sys.exit(1)

    posts = await asyncio.gather(ahttp.parse_bitrix())

    # попытка распарсить вк, в случае, если токен недействителен - завершение программы
    try:
        vk_posts = parser.parse_vk()
    except NoTokenError as e:
        print(e.txt, file=sys.stderr)
        sys.exit(1)

    for post in posts[0] + vk_posts:
        text = '\n'.join(list(filter(lambda x: isinstance(x, str), post))).replace('\\n', '\n')
        author, date = post[0]
        attachments = list(map(lambda y: y[0], filter(lambda x: isinstance(x, tuple), post[1:])))
        my_worker.add_post(author, text, attachments, date)

    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    gui = MyGUI(my_worker)
    gui.show()
    sys.exit(app.exec())


def except_hook(tp, value, traceback):
    sys.excepthook(tp, value, traceback)


if __name__ == '__main__':
    asyncio.run(main())
