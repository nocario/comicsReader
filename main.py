import os
import sys
import qdarkgraystyle
import qdarkstyle
import qtmodern.styles
import qtmodern.windows
import tempfile
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtPrintSupport
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtWidgets import *
from Preparinator import *
from Qmedia import *
from _thread import start_new_thread

database = sqlite3.connect('datasql.db')
curseur = database.cursor()
curseur.execute("""CREATE TABLE IF NOT EXISTS info (cover BLOP, title, author, year, tags, quality,name_id)""")
database.commit()


class Table(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('library')
        self.layout = QtWidgets.QGridLayout()
        self.table = QTableWidget()
        self.data_row = []
        self.setCentralWidget(self.table)
        self.resize(750, 400)

        self.button_edit = QtWidgets.QPushButton('edit')
        self.button_delete = QtWidgets.QPushButton('delete')

        self.button_edit.clicked.connect(self.edit)
        self.button_delete.clicked.connect(self.delete)

        self.layout.addWidget(self.button_edit, 1, 9, 1, 1)
        self.layout.addWidget(self.button_delete, 2, 9, 1, 1)
        self.layout.addWidget(self.table, 1, 1, 6, 6)

        self.setCentralWidget(QtWidgets.QFrame())
        self.centralWidget().setLayout(self.layout)
        self.table.itemSelectionChanged.connect(self.row_data)

        self.table.resizeRowsToContents()

    def row_data(self):
        x = self.table.currentRow()
        if x != -1:
            self.data_row = [self.table.item(x, i).text() for i in range(1, 7)]  # PEP 289

    def fill(self):
        self.table.clear()
        labels = ['COVER', 'TITLE', 'AUTHOR', 'YEAR', 'TAGS', 'QUALITY']
        self.table.setColumnCount(len(labels) + 1)
        self.table.setColumnHidden(6, True)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(labels)

        for i in range(0, self.table.columnCount() - 1):
            self.table.setColumnWidth(i, 265)

        with sqlite3.connect('datasql.db') as connect:
            for cover, title, author, year, tags, quality, name_id in connect.execute(
                    "SELECT cover, title, author,year,tags,quality,name_id FROM info"):
                row = self.table.rowCount()
                self.table.setRowCount(row + 1)
                image_label = self.get_image_label(cover)
                self.table.setCellWidget(row, 0, image_label)
                self.table.setItem(row, 1, QTableWidgetItem(title))
                self.table.setItem(row, 2, QTableWidgetItem(author))
                self.table.setItem(row, 3, QTableWidgetItem(year))
                self.table.setItem(row, 4, QTableWidgetItem(tags))
                self.table.setItem(row, 5, QTableWidgetItem(quality))
                self.table.setItem(row, 6, QTableWidgetItem(name_id))
                self.table.setRowHeight(row, 320)
        connect.close()

    @staticmethod
    def get_image_label(image):
        pixmap = QPixmap()
        image_label = QLabel("")
        image_label.setScaledContents(True)
        pixmap.loadFromData(image)
        image_label.setPixmap(pixmap)
        return image_label

    def edit(self):
        if self.table.currentRow() != -1:
            self.widget_edit = Edit()

    def delete(self):
        if self.table.currentRow() != -1:
            delete = self.table.item(self.table.currentRow(), 6).text()
            curseur.execute("""DELETE FROM info WHERE name_id = ?;""", (delete,))
            database.commit()
            self.table.removeRow(self.table.currentRow())


class Edit(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Edit Metadata')
        self.resize(300, 450)
        self.list_widget = QtWidgets.QListWidget()
        self.layout = QtWidgets.QGridLayout()
        self.setCentralWidget(QtWidgets.QFrame())
        self.centralWidget().setLayout(self.layout)

        self.title_label = QtWidgets.QLabel('Title :')
        self.author_label = QtWidgets.QLabel('Author :')
        self.year_label = QtWidgets.QLabel('Year :')
        self.tags_label = QtWidgets.QLabel('Tags :')
        self.quality_label = QtWidgets.QLabel('Quality :')  # line edit à cote de label

        self.title = QtWidgets.QLineEdit(window.bib.data_row[0])
        self.author = QtWidgets.QLineEdit(window.bib.data_row[1])
        self.year = QtWidgets.QLineEdit(window.bib.data_row[2])
        self.tags = QtWidgets.QLineEdit(window.bib.data_row[3])
        self.quality = QtWidgets.QLineEdit(window.bib.data_row[4])
        self.name_id = window.bib.data_row[5]

        self.button_save = QtWidgets.QPushButton('save')
        self.button_save.clicked.connect(self.save)

        self.layout.addWidget(self.button_save, 20, 1, 3, 6)

        self.layout.addWidget(self.title_label, 4, 1, 1, 12)
        self.layout.addWidget(self.author_label, 7, 1, 1, 12)
        self.layout.addWidget(self.year_label, 10, 1, 1, 12)
        self.layout.addWidget(self.tags_label, 13, 1, 1, 12)
        self.layout.addWidget(self.quality_label, 16, 1, 1, 12)

        self.layout.addWidget(self.title, 5, 1, 2, 12)
        self.layout.addWidget(self.author, 8, 1, 2, 12)
        self.layout.addWidget(self.year, 11, 1, 2, 12)
        self.layout.addWidget(self.tags, 14, 1, 2, 12)
        self.layout.addWidget(self.quality, 17, 1, 2, 12)

        self.show()

    def save(self):  # on recupere le texte de line edit
        title = self.title.text()
        author = self.author.text()
        year = self.year.text()
        tags = self.tags.text()
        quality = self.quality.text()
        name_id = window.bib.data_row[5]

        try:
            if int(quality) > 5:
                quality = '5'
            elif int(quality) < 0:
                quality = '0'
        except ValueError:
            quality = None

        if not year.isdigit():
            year = None

        query = """UPDATE info SET title=?,author=?,year=?,tags=?,quality=? WHERE name_id=?"""
        curseur.execute(query, (title, author, year, tags, quality, name_id))
        database.commit()
        with sqlite3.connect('datasql.db') as connect:
            row = window.bib.table.currentRow()
            for title, author, year, tags, quality in connect.execute(
                    "SELECT title, author,year,tags,quality FROM info WHERE name_id=?", (name_id,)):
                window.bib.table.setItem(row, 1, QTableWidgetItem(title))
                window.bib.table.setItem(row, 2, QTableWidgetItem(author))
                window.bib.table.setItem(row, 3, QTableWidgetItem(year))
                window.bib.table.setItem(row, 4, QTableWidgetItem(tags))
                window.bib.table.setItem(row, 5, QTableWidgetItem(quality))
        connect.close()


class EditWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.hbox = QHBoxLayout()
        self.leftlist = QListWidget()

        self.leftlist.insertItem(3, "Blue Dark style")
        self.leftlist.insertItem(4, "Dark Style")
        self.leftlist.insertItem(5, "Light Style")
        self.leftlist.insertItem(6, "Dark Grey Style")

        self.leftlist.itemClicked.connect(self.new_style)
        self.hbox.addWidget(self.leftlist)
        self.setLayout(self.hbox)

    @staticmethod
    def new_style(item):
        if item.text() == 'Blue Dark style':
            style = qdarkstyle.load_stylesheet()
            window.conf.setValue('style', style)
            app.setStyleSheet(style)
        elif item.text() == 'Dark Style':
            qtmodern.styles.dark(app)
            window.conf.setValue('style', 1)
        elif item.text() == 'Light Style':
            qtmodern.styles.light(app)
            window.conf.setValue('style', 0)
        elif item.text() == 'Dark Grey Style':
            style2 = qdarkgraystyle.load_stylesheet()
            window.conf.setValue('style', style2)
            app.setStyleSheet(style2)


class TabTable(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def close_tab(self, index):
        tab = self.tabs.widget(index)
        if not tab.windowTitle() == 'library':
            tab.deleteLater()
        self.tabs.removeTab(index)


class Window(QWidget):  # class qui crée le widget ou l'on lis la bande déssiné
    def __init__(self, comics):
        super().__init__()
        self.layout = QGridLayout()
        self.comics = comics
        self.num_page = 0
        self.label_img = QLabel()
        self.pixmap = QPixmap()
        _next = QPushButton("next")
        _next.setShortcut(QKeySequence("Right"))
        previous = QPushButton("previous")
        previous.setShortcut(QKeySequence("Left"))
        self.scroll = QScrollArea()
        _next.clicked.connect(self.next_previous)
        previous.clicked.connect(self.next_previous)
        self.page = QLabel()
        self.page.setText('page : ' + str(self.num_page))

        self.current_size = self.size()

        self.layout.addWidget(_next, 1, 2)
        self.layout.addWidget(previous, 1, 1)
        self.layout.addWidget(self.page, 1, 0)
        self.layout.addWidget(self.gen_btn(len(self.comics.comic.generate_content())), 0, 0)
        self.layout.addWidget(self.label_image(), 0, 1, 1, 2)
        self.setLayout(self.layout)

    def gen_btn(self, n):
        group_box = QGroupBox("bouton")
        group_box.setFixedWidth(200)
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(group_box)
        vbox = QVBoxLayout()
        cmp = 0
        for i in range(0, n):
            btn = QPushButton(str(cmp))
            btn.setFixedWidth(100)
            cmp += 1
            btn.clicked.connect(self.pages)
            vbox.addWidget(btn)
        vbox.setSpacing(10)
        group_box.setLayout(vbox)
        scroll.setFixedWidth(200)
        return scroll

    def label_image(self):
        group_box = QGroupBox("image")
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.widgetResizable()
        scroll.setWidgetResizable(True)
        scroll.setWidget(group_box)
        vl = QVBoxLayout()

        self.pixmap.load(str(Path.cwd() / Path(self.comics.comic.temp.name).name / self.comics.comic.Path.stem /
                             self.comics.comic.generate_content()[0]))
        self.label_img.setPixmap(self.pixmap)
        self.label_img.setAlignment(Qt.AlignCenter)
        self.label_img.resize(640, 480)
        vl.addWidget(self.label_img)
        group_box.setLayout(vl)
        return scroll

    def pages(self):
        self.num_page = int(self.sender().text())
        self.pixmap.load(str(Path.cwd() / Path(self.comics.comic.temp.name).name / self.comics.comic.Path.stem /
                             self.comics.comic.generate_content()[self.num_page]))
        self.label_img.setPixmap(self.pixmap.scaled(self.current_size,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        self.page.setText('page : ' + str(self.num_page))

    def next_previous(self):
        if self.sender().text() == "next":
            if self.num_page < len(self.comics.comic.generate_content()) - 1:
                self.num_page += 1
                self.pixmap.load(str(Path.cwd() / Path(self.comics.comic.temp.name).name / self.comics.comic.Path.stem /
                                     self.comics.comic.generate_content()[self.num_page]))
                self.label_img.setPixmap(self.pixmap.scaled(self.current_size,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        elif self.num_page > 0:
            self.num_page -= 1
            self.pixmap.load(str(Path.cwd() / Path(self.comics.comic.temp.name).name / self.comics.comic.Path.stem /
                                 self.comics.comic.generate_content()[self.num_page]))
            self.label_img.setPixmap(self.pixmap.scaled(self.current_size,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        self.page.setText('page : ' + str(self.num_page))

    def zoom(self):
        self.current_size *= 1.25
        self.label_img.setPixmap(self.pixmap.scaled(self.current_size,Qt.KeepAspectRatio,Qt.SmoothTransformation))

    def zoom_out_(self):
        self.current_size *= 0.8
        self.label_img.setPixmap(self.pixmap.scaled(self.current_size,Qt.KeepAspectRatio,Qt.SmoothTransformation))

    def resizeEvent(self, event):
        self.current_size = self.size()
        pixmap = self.pixmap.scaled(event.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation)
        self.label_img.setPixmap(pixmap)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent, flags=QtCore.Qt.Window)
        self.setGeometry(500, 500, 570, 600)
        self.setWindowTitle('Doubaeva Ghidini comics reader')
        self.conf = QSettings('style')

        self.bib = Table()

        self.tabs = TabTable()
        self.menu()
        self.app_style()

        self.printer = QtPrintSupport.QPrinter()
        self.setCentralWidget(self.tabs)

    def menu(self):
        tool_bar = QtWidgets.QToolBar()

        # menu file
        menu_file = self.menuBar().addMenu('File')
        action = menu_file.addAction('Оpen', self.open, QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        tool_bar.addAction(action)
        action.setStatusTip('Open')
        menu_file.addSeparator()
        action = menu_file.addAction('Library', self.f_library, QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        tool_bar.addAction(action)
        menu_file.addSeparator()
        menu_file.addAction('Ext', QtWidgets.qApp.quit, QtCore.Qt.Key_Escape)

        # menu edit
        menu_edit = self.menuBar().addMenu('Edit')
        menu_edit.addAction('Change Window Style', self.f_edit, QtCore.Qt.CTRL + QtCore.Qt.Key_E)

        # menu view
        menu_view = self.menuBar().addMenu('View')
        action = menu_view.addAction('Zoom in', self.zoom_in, QKeySequence("+"))
        tool_bar.addAction(action)
        action = menu_view.addAction('Zoom out', self.zoom_out, QKeySequence("-"))
        tool_bar.addAction(action)

        # menu music
        menu_music = self.menuBar().addMenu('Music')
        action = menu_music.addAction('Music Player', self.f_read, QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        tool_bar.addAction(action)

        # menu print
        menu_print = self.menuBar().addMenu('Print')
        action = menu_print.addAction('Print', self.print, QtCore.Qt.CTRL + QtCore.Qt.Key_P)
        tool_bar.addAction(action)
        menu_print.addAction('Page setup', self.page_setup)

        # menu help
        menu_help = self.menuBar().addMenu('Help')
        action = menu_help.addAction('Help...', self.f_help, QtCore.Qt.CTRL + QtCore.Qt.Key_H)
        tool_bar.addAction(action)

        tool_bar.setMovable(False)
        tool_bar.setFloatable(False)
        self.addToolBar(tool_bar)

        status_bar = self.statusBar()
        status_bar.setSizeGripEnabled(False)

    def open(self):
        image_path, _ = QFileDialog.getOpenFileName(filter='(*.cbz);;(*.cbr)')

        if image_path != '':
            self.comics = PrepComics(image_path)

            try:
                self.tabs.tabs.removeTab(self.tabs.tabs.indexOf(self.bib))
            except AttributeError:
                pass

            self.tabs.tabs.addTab(Window(self.comics), self.comics.comic.Path.stem)

    def app_style(self):
        value = self.conf.value('style')
        if not value:
            qtmodern.styles.light(app)
        elif type(value) == str:
            app.setStyleSheet(self.conf.value('style'))
        elif value == 0:
            qtmodern.styles.light(app)
        else:
            qtmodern.styles.dark(app)

    def print(self):
        p = QtPrintSupport.QPrintDialog(self.printer, parent=self)
        p.setOptions(
            QtPrintSupport.QAbstractPrintDialog.PrintToFile | QtPrintSupport.QAbstractPrintDialog.PrintSelection)
        try:
            if p.exec() == QtWidgets.QDialog.Accepted:
                self.layout.print(self.printer)
        except AttributeError:
            QtWidgets.QMessageBox.information(self, '', 'non fonctionnel')

    def page_setup(self):
        pd = QtPrintSupport.QPageSetupDialog(self.printer, parent=self)
        pd.exec()

    def zoom_in(self):
        try:
            self.tabs.tabs.currentWidget().zoom()  # 288
        except AttributeError:
            pass

    def zoom_out(self):
        try:
            self.tabs.tabs.currentWidget().zoom_out_()  # 293
        except AttributeError:
            pass

    @staticmethod
    def f_edit():
        dialog = EditWindow()
        dialog.exec_()

    def f_library(self):
        self.bib.table.setRowCount(0)
        self.bib.fill()
        self.tabs.tabs.addTab(self.bib, 'Library')

    def f_read(self):
        media = MyWindow()
        self.tabs.tabs.addTab(media, 'Media Player')

    def f_help(self):
        QtWidgets.QMessageBox.about(self, 'à propos de e-comic',
                                    '<center>e-comic 1.0.0<br><br>'
                                    'application de liseuses de bandes dessinées au format numérique '
                                    'basée sur la librairie PyQt5 <br><br>'
                                    '☼  Ghidini Doubaeva')


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
