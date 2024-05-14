"""GUI приложения."""
import os
import sys
import datetime as dt
import vk_parser
from async_http import save_by_url
from my_tracebacks import NoTokenError
# from PyQt5 import uic
from my_gui import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog


class MyGUI(QMainWindow, Ui_MainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.manager = data_manager
        # uic.loadUi('gui\\gui.ui', self)
        self.setupUi(self)

        # настраиваем внешний вид столбцов
        header1 = self.table.horizontalHeader()
        header1.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header1.setSectionResizeMode(1, QHeaderView.Stretch)
        header1.setSectionResizeMode(2, QHeaderView.Stretch)
        header1.setSectionResizeMode(3, QHeaderView.Stretch)

        # задать функции кнопок
        self.search.clicked.connect(self.showData)
        self.showChosen.clicked.connect(self.showChosenPost)
        self.save.clicked.connect(self.saveFile)

        self.start_parsing()

        # отображаем актуальную информацию
        self.loadBoxes()
        self.showData()

    def start_parsing(self):
        """Поскольку изначальный парсинг VK требует ввода токена, то необходимо получить его
        от пользователя."""
        parser = None
        try:
            parser = vk_parser.Parser()
        except NoTokenError as e:
            res, status = QInputDialog.getText(self, 'Настройка токена',
                                               'Введите access_token для VK (см. в документации,\n'
                                               'необходимо получить доступ к группам пользователя)')
            if status:
                try:
                    parser = vk_parser.Parser(first_try=False)
                    parser.add_token(res)
                except NoTokenError as e:
                    QMessageBox.critical(self, 'Ошибка', e.txt)
                    return
            else:
                QMessageBox.critical(self, 'Ошибка', e.txt)
                return

        try:
            vk_posts = parser.parse_vk()
        except NoTokenError as e:
            QMessageBox.critical(self, 'Ошибка', e.txt)
            return

        for post in vk_posts:
            text = '\n'.join(list(filter(lambda x: isinstance(x, str), post))).replace('\\n', '\n')
            author, date = post[0]
            attachments = list(map(lambda y: (y[0], y[-1]), filter(lambda x: isinstance(x, tuple),
                                                                   post[1:])))
            self.manager.add_post(author, text, attachments, date)

    def loadBoxes(self):
        """Подгрузить все данные для фильтрации."""
        self.authorBox.addItems(self.manager.get_authors())
        self.dateBox.addItems(self.manager.get_dates())
        self.fileBox.addItems(self.manager.get_attachments())

    def getFilteredData(self):
        """Вернуть отфильтрованную по введенным параметрам информацию"""
        author = self.authorBox.currentText()
        date_text = self.dateBox.currentText()
        use_date, use_author = False, False
        au_id, date = None, None

        if date_text != 'Выберите дату':
            date_ex = dt.datetime.strptime(date_text, '%d.%m.%y')
            date = dt.date(year=date_ex.year, month=date_ex.month, day=date_ex.day)
            use_date = True

        if author != 'Выберите автора':
            au_id = self.manager.get_author_by(name=author)
            use_author = True

        if use_date and use_author:
            posts = self.manager.get_posts(author_id=au_id, date=date)
        elif use_date:
            posts = self.manager.get_posts(date=date)
        elif use_author:
            posts = self.manager.get_posts(author_id=au_id)
        else:
            posts = self.manager.get_posts()
        return posts

    def updateFileBox(self, posts):
        """Обновить ссылки в соответствии с выбранными постами."""
        self.fileBox.clear()
        self.fileBox.addItem('Выберите файл')
        for post in posts:
            self.fileBox.addItems(self.manager.get_attachments(post[0]))

    def showData(self):
        """Загрузить в таблицу всю информацию из базы данных, с учетом фильтров."""
        posts = self.getFilteredData()
        self.updateFileBox(posts)
        self.table.setRowCount(0)
        for i, row in enumerate(posts):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))

    def showChosenPost(self):
        """Показать пост, который выбрали в таблице."""
        if self.table.currentRow() >= 0:
            self.postView.clear()
            row = self.table.currentRow()
            post_id = int(self.table.item(row, 0).text())
            post_text = self.manager.get_post_by_id(post_id)
            attachments = self.manager.get_attachments(post_id=post_id)
            post_text += '\n\nПрикрепленные файлы:\n' + '\n'.join(map(lambda x: f'{x[0]}) {x[1]}',
                                                                      enumerate(attachments, 1)))
            self.postView.appendPlainText(post_text)
            self.updateFileBox([(post_id,)])
        else:
            QMessageBox.warning(self, 'Невозможно', 'Не выбран элемент для просмотра.',
                                defaultButton=QMessageBox.Ok)

    def saveFile(self):
        """Выбрасывает исключение со ссылкой в тексте, чтобы основная функция все сохранила."""
        url = self.fileBox.currentText()
        if url != 'Выберите файл':
            filename = self.manager.get_attachment_filename(url)
            filepath = QFileDialog.getSaveFileName(self, 'Выберите место для сохранения файла.',
                                                   os.getcwd() + '\\saves\\' + filename)[0]
            try:
                # print(url, filepath)
                save_by_url(url, filepath)
            except Exception as e:
                print(e)
                QMessageBox.critical(self, 'Ошибка', 'Не удалось сохранить файл.',
                                     defaultButton=QMessageBox.Ok)

    def closeEvent(self, a0):
        self.manager.close_session()


def except_hook(tp, value, traceback):
    sys.excepthook(tp, value, traceback)

