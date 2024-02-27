"""GUI приложения."""
import sys
import datetime as dt
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableWidgetItem
from my_tracebacks import NeedSave


class MyGUI(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.manager = data_manager
        uic.loadUi('gui\\gui.ui', self)
        # self.setupUi()

        # настраиваем внешний вид столбцов
        header1 = self.table.horizontalHeader()
        header1.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header1.setSectionResizeMode(1, QHeaderView.Stretch)
        header1.setSectionResizeMode(2, QHeaderView.Stretch)
        header1.setSectionResizeMode(3, QHeaderView.Stretch)

        # инициализируем statusbar
        self.status = self.statusBar()

        # задать функции кнопок
        self.search.clicked.connect(self.showData)
        self.showChosen.clicked.connect(self.showChosenPost)
        self.save.clicked.connect(self.saveFile)

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

    def showData(self):
        """Загрузить в таблицу всю информацию из базы данных, с учетом фильтров."""
        posts = self.getFilteredData()
        self.table.setRowCount(0)
        for i, row in enumerate(posts):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setElem(i, j, QTableWidgetItem(str(elem)))

    def showChosenPost(self):
        """Показать пост, который выбрали в таблице."""
        if self.table.selestedItems():
            self.postView.clear()
            post_id = int(self.table.selestedItems()[0].text())
            post_text = self.table.selestedItems()[1].text()
            attachments = self.manager.get_attachments(post_id=post_id)
            post_text += '\n\nПрикрепленные файлы:\n' + '\n'.join(map(lambda x: f'{x[0]}) {x[1]}',
                                                                      enumerate(attachments)))
            self.postView.appendPlainText(post_text)
        else:
            self.status.showMessage('Не выбран элемент для просмотра.', 5000)

    def saveFile(self):
        """Выбрасывает исключение со сслыкой в тексте, чтобы основная функция все сохранила."""
        text = self.fileBox.currentText()
        if text != 'Выберите файл':
            raise NeedSave(text)
        self.status.showMessage('Невозможно сохранить данный файл.', 5000)


def except_hook(tp, value, traceback):
    sys.excepthook(tp, value, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    gui = MyGUI()
    gui.show()
    sys.exit(app.exec())
