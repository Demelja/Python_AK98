#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
There is Analizator / Visualization tool for log-files from AK98
Dmytro Melnychenko had made this.
06-JAN-2022 is the first day
"""

##-- log analizer
##-- Dmytro Melnychenko AKA D-Man
##-- program name - ?




#-- libraries
import os
import sys
import threading
import tempfile
import shutil
import zipfile
from PyQt5.QtCore import QStringListModel

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QFileDialog, QApplication)
from PyQt5.QtGui import QIcon

from PyQt5.Qt import (
QApplication, QWidget, QSplitter, QTreeView, QTextEdit, 
QFileSystemModel, QVBoxLayout, QDir
)











class LogAnalizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Direct tree')

        self.model = QFileSystemModel()
        self.model.setFilter(
            QDir.AllDirs |
#            QDir.NoDotAndDotDot |
            QDir.Files
        )
        self.model.setRootPath(QDir.currentPath())

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index('.'))
        
        self.tree.setColumnWidth(0,250)
        # Don't show columns for size, file type, and last modified
        self.tree.setHeaderHidden(True)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)

        self.tree.clicked.connect(self._on_single_clicked)
        self.tree.doubleClicked.connect(self._on_double_clicked)
        
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.setAlternatingRowColors(True)

        self.textEdit = QTextEdit()

        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.textEdit)
        splitter.setSizes([250, 100])

        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        """
		self.model = QFileSystemModel()
		self.model.setRootPath(dir_path)
		self.tree =  QTreeView()
		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(dirPath))
		self.tree.setColumnWidth(0, 250)
		self.tree.setAlternatingRowColors(True)

		layout = QVBoxLayout()
		layout.addWidget(self.tree)
		self.setLayout(layout)
        """





    ''' функция для обработки события single-клика '''
    def _on_single_clicked(self, index):
        # the signal passes the index of the clicked item
        dir_path = self.model.filePath(index)
        root_index = self.model.setRootPath(dir_path)
        self.tree.setRootIndex(root_index)


    ''' функция для обработки события double-клика '''
    def _on_double_clicked(self, index):
        file_name = self.model.filePath(index)

        """
        with open(file_name, encoding='utf-8') as f:
            text = f.read()
            self.textEdit.setPlainText(text)
        """
        """ 1. проверка - является ли кликнутое файлом и архивом, причем не более 1 МБ размером
               - если нет, сообщить "не архив" или "это архив архивов, распакуйте сначала"
               - если да, запустить далее """
               
        """
                2. создать временный каталог
        """
        """
                3. скопировать туда этот архив и распаковать
        """
        """
                4. перейти в папку eMMC2/logdata/blackbox/
        """
        """
                5. проверить наличие файла ak98.log.txt. Если не найден - сообщить и выйти
                  Если найден, запустить далее
        """
        """
                    1. создать файл базы данных
        """
        """
                    2. открыть ak98.log.txt и считать его построчно
        """
        """
                    3. для каждой строки:
        """
        """
                    3.1. разделить по пробелу
        """
        """
                    3.1.1. для элемента [0]: разделить по "-"
                             для элемента [0]: разделить по "."
                                               сравнить с "предыдущим" значением. Если НЕ СОВПАДАЕТ - создать новую строку в БД
                               для элемента [0]: преобразовать в дату и время, записать в БД
                               для элемента [1]: записать в БД
        """
        """
                    3.1.2. если элемент [1] равен строке "CONTROL_TRACO", записать в БД элемент [5] в соответствующий столбец, а элемент [7] - в столбец "VALUE"
                    3.1.3. если элемент [1] равен строке "UI_CANLOG" AND элемент [3] не равен "MACHINEMODE_UI" AND элемент [4] не равен "DIAGNOSTIC_RAISED", 
                           записать в БД элемент [4] в соответствующий столбец, а элемент [5] - в столбец "VALUE"
        """

    ''' функция для обработки события клика в root '''

    ''' функция для обработки события клика в папку '''

    ''' функция для обработки события single-клика в zip '''







''' ==================================================================== '''
if __name__ == "__main__":
    app = QApplication([])

    win = LogAnalizer()
    win.resize(600, 400)
    win.show()

    sys.exit(app.exec())
















"""
class LOG_Analizer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')

        openFile = QAction(QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.openZipDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        #self.show()
        self.dir_content()

    # функция для определения содержимого текущей директории
    def dir_content(self):
        ''' функция для определения содержимого текущей директории'''
	    # содержимое в текущей директории
        dir_list = os.listdir(self.path_text.get())
        path = self.path_text.get()


    def openZipDialog(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]

        print(fname)
        print(os.path.dirname(fname))
        with open("hello.txt", "w") as file_result:
            file_result.writelines("First Line")
        print(file_result)

        # создаём временную директорию
        with tempfile.TemporaryDirectory() as directory:
            print('Создана временная директория %s' % directory)
            try:
                shutil.copyfile(fname, os.path.join(directory, "log_file_packed"))
            except IOError:
                print("Copy failed")
            else:
                print("Copied!", str(os.path.join(directory, "log_file_packed")))
            # после копирования -> распаковка
            with zipfile.ZipFile(os.path.join(directory, "log_file_packed"), 'r') as archive:
                archive.extractall(directory)
            print("Extracted!", str(archive))
            print(os.listdir(path=directory))


        "" "
        fdirectory = os.path.dirname(fname)
        list_of_files = os.listdir(fdirectory)

        for file in list_of_files:
            print(file, "----------------------")

            # создаём временную директорию
            with tempfile.TemporaryDirectory() as directory:
                print('Создана временная директория %s' % directory)
                try:
                    shutil.copyfile(fname, os.path.join(directory, "log_file_packed"))
                except IOError:
                    print("Copy failed")
                else:
                    print("Copied!", str(os.path.join(directory, "log_file_packed")))
                archive = tarfile.open(os.path.join(directory, "log_file_packed"), "r:gz")
                archive.extractall(directory)
                print("Extracted!", str(archive))
                print(os.listdir(path=directory))
                f_events = [f for f in os.listdir(path=directory) if f.endswith('.PLE')]
                print(f_events)
                file_data = f_events[0]
                print(file_data)
                # получим объект файла
                file = open(os.path.join(directory, file_data), mode="r", encoding="utf-16")
                
                # считываем все строки
                content = file.readlines()
                # известно, что первые 27 строк - общая информация, пропускаем их
                for i in range(27): content.pop(0)

                # записать в переменную время начала сеанса
                therapy_start = (content[0].strip().split(";"))[1]
                
                # поиск вхождений искомого текста в строке
                for line in content:
                    # разбить строку на элементы
                    element = (line.strip()).split(";")
                    # записать в переменную время завершения сеанса
                    therapy_finish = element[1]
                    if element[4] == '90' or element[4] == '91' or element[4] == '97' or element[4] == '93' or element[4] == '94' or element[4] == '95':
                        print(element, "   ", file_result)
                        #Запишем некоторую информацию в файл "hello.txt":
                        with open("hello.txt", "a") as file_result:
                            file_result.writelines(element)
                        #Если мы откроем папку, в которой находится текущий скрипт Python, то увидем там файл hello.txt.
                
                #datetime.strptime('2014-11-17 00:00:00', '%Y-%m-%d %H:%M:%S')
                
                print(therapy_start, " -- ", therapy_finish)

                output_text = therapy_start + " -- " + therapy_finish

                self.textEdit.setText(output_text)

                # закрываем файл
                file.close
        
        #file_result.close()
        "" "


        "" "
        # создаём временную директорию
        with tempfile.TemporaryDirectory() as directory:
            print('Создана временная директория %s' % directory)
            try:
                shutil.copyfile(fname, os.path.join(directory, "log_file_packed"))
            except IOError:
                print("Copy failed")
            else:
                print("Copied!", str(os.path.join(directory, "log_file_packed")))
            archive = tarfile.open(os.path.join(directory, "log_file_packed"), "r:gz")
            archive.extractall(directory)
            print("Extracted!", str(archive))
            print(os.listdir(path=directory))
            f_events = [f for f in os.listdir(path=directory) if f.endswith('.PLE')]
            print(f_events)
            file_data = f_events[0]
            print(file_data)
            # получим объект файла
            file = open(os.path.join(directory, file_data), mode="r", encoding="utf-16")
            
            # считываем все строки
            content = file.readlines()
            # известно, что первые 27 строк - общая информация, пропускаем их
            for i in range(27): content.pop(0)

            # записать в переменную время начала сеанса
            therapy_start = (content[0].strip().split(";"))[1]
            
            # поиск вхождений искомого текста в строке
            for line in content:
                # разбить строку на элементы
                element = (line.strip()).split(";")
                # записать в переменную время завершения сеанса
                therapy_finish = element[1]
                if element[4] == '90' or element[4] == '91':
                    print(element)
            
            #datetime.strptime('2014-11-17 00:00:00', '%Y-%m-%d %H:%M:%S')
            " ""
            Запишем некоторую информацию в файл "hello.txt":
            with open("hello.txt", "w") as file:
                file.write("hello world")
            Если мы откроем папку, в которой находится текущий скрипт Python, то увидем там файл hello.txt.
            " ""
            
            print(therapy_start, " -- ", therapy_finish)

            output_text = therapy_start + " -- " + therapy_finish

            self.textEdit.setText(output_text)

            # закрываем файл
            file.close
        "" "

        "" "
        f = open(fname, 'r')

        with f:
            data = f.read()
            self.textEdit.setText(data)
        "" "



if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = LOG_Analizer()
    sys.exit(app.exec_())
"""