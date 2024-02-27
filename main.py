import sys
import asyncio
import async_http as ahttp
import vk_parser as pp
import db_worker
from gui import MyGUI
from PyQt5.QtWidgets import QApplication
from my_tracebacks import NeedSave, NoTokenError


async def main():
    my_worker = db_worker.Worker('db\\test-0-1.db')
    parser = pp.Parser()
    posts = await asyncio.gather(ahttp.parse_bitrix())
    vk_posts = parser.parse_vk()

    for post in posts + vk_posts:
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
    if tp == NeedSave:
        pass  # TODO: придумать блять что с этим делать, как запустить корутину не через корутины !!!
    sys.excepthook(tp, value, traceback)


if __name__ == '__main__':
    asyncio.run(main())
