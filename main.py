import sys
import asyncio
import async_http as ahttp
import db_worker
from gui import MyGUI
from PyQt5.QtWidgets import QApplication


async def main():
    my_worker = db_worker.Worker('db\\db_v1.db')

    posts = await asyncio.gather(ahttp.parse_bitrix())

    for post in posts[0]:
        text = '\n'.join(list(filter(lambda x: isinstance(x, str), post))).replace('\\n', '\n')
        author, date = post[0]
        attachments = list(map(lambda y: (y[0], y[-1]), filter(lambda x: isinstance(x, tuple),
                                                               post[1:])))
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
