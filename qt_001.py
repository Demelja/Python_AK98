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

import sqlite3



## секция хардкорных значений
### 
file_data = "ak98.log.txt"
### перечень (кортеж ?) кодов параметров
### fields = ( 2256, 3345 )








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

        self.tree.clicked.connect(self.fn_on_single_clicked)
        self.tree.doubleClicked.connect(self.fn_on_double_clicked)
        
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






    ''' функция для обработки события single-клика '''
    def fn_on_single_clicked(self, index):
        # the signal passes the index of the clicked item
        dir_path = self.model.filePath(index)
        root_index = self.model.setRootPath(dir_path)
        self.tree.setRootIndex(root_index)





    ''' функция для обработки события double-клика '''
    def fn_on_double_clicked(self, index):
        file_name = self.model.filePath(index)
        """ 1. проверка - является ли кликнутое файлом и архивом, причем не более 1 МБ размером
               - если нет, сообщить "не архив" или "это архив архивов, распакуйте сначала"
               - если да, запустить далее """
        # создаём временную директорию
        with tempfile.TemporaryDirectory() as directory:
            print('Создана временная директория %s' % directory)
            try:
                shutil.copyfile(file_name, os.path.join(directory, "log_file_packed"))
            except IOError:
                print("Copy failed")
            else:
                print("Copied!", str(os.path.join(directory, "log_file_packed")))
            # после копирования -> распаковка
            with zipfile.ZipFile(os.path.join(directory, "log_file_packed"), 'r') as archive:
                archive.extractall(directory)
            print("Extracted!", str(archive))
            print(os.listdir(path=directory))
            """
                    4. перейти в папку eMMC2/logdata/blackbox/
            """
            directory = os.path.join(directory, "eMMC2")
            directory = os.path.join(directory, "LogArchive")
            directory = os.path.join(directory, os.path.splitext(os.path.basename(file_name))[0])
            directory = os.path.join(directory, "logdata")
            directory = os.path.join(directory, "blackbox")
            print(os.listdir(path=directory))
            """
                    5. проверить наличие файла ak98.log.txt. Если не найден - сообщить и выйти
                    Если найден, запустить далее
            """
            """
                        1. создать файл базы данных
            """
            fn_sql_connection()
            """
                        2. открыть ak98.log.txt и считать его построчно
            """
            # получим объект файла
            #
            file = open(os.path.join(directory, file_data), mode="r", encoding="utf-8")
            
            # считываем все строки
            content = file.readlines()

            # поиск вхождений искомого текста в строке
            """
                        3. для каждой строки:
            """
            date_time_prior = ""
            for line in content:
                # разбить строку на элементы
                """
                            3.1. разделить по пробелу
                """
                element = (line.strip()).split(" ")

                """
                            3.1.1. для элемента [0]: разделить по "-"
                                    для элемента [0]: разделить по "."
                                                    сравнить с "предыдущим" значением. Если НЕ СОВПАДАЕТ - создать новую строку в БД
                                    для элемента [0]: преобразовать в дату и время, записать в БД
                                    для элемента [1]: записать в БД
                """
                date_time = (element[0].split("-"))[0].split(".")[0]
                if ( date_time_prior != date_time ):
                    print(element[0], date_time, (element[0].split("-"))[0].split(".")[1])
                    date_time_prior = date_time
                else:
                    print("+++       ", date_time)
                
                """
                            3.1.2. если элемент [1] равен строке "CONTROL_TRACO", записать в БД элемент [5] в соответствующий столбец, а элемент [7] - в столбец "VALUE"
                            3.1.3. если элемент [1] равен строке "UI_CANLOG" AND элемент [3] не равен "MACHINEMODE_UI" AND элемент [4] не равен "DIAGNOSTIC_RAISED", 
                                записать в БД элемент [4] в соответствующий столбец, а элемент [5] - в столбец "VALUE"

                                if ( $record_line -like "*MailErrorGlobal*" ) {
                                    #Write-Host $record_line
                                    #$record_line | Out-File -Append $ArchiveFile
                                    $str_datetime = $record_line.Substring( 0, 28 )
                                    $str_node = $record_line.Substring( $record_line.IndexOf( "nodeNumber" ) + 11, 1 )
                                    $str_errcategory = $record_line.Substring( $record_line.IndexOf( "errCategory" ) + 12, 2 )
                                    if ( $str_errcategory[1] -eq "," ) { $str_errcategory = "0" + $str_errcategory[0] }

                                    $str_errsubcategory = $record_line.Substring( $record_line.IndexOf( "errSubCategory" ) + 15, 2 )
                                    if ( $str_errsubcategory[1] -eq "," ) { $str_errsubcategory = "0" + $str_errsubcategory[0] }
                                    
                                    $str_errindex = $record_line.Substring( $record_line.IndexOf( "errIndex" ) + 9, 2 )
                                    if ( $str_errindex[1] -eq "," ) { $str_errindex = "0" + $str_errindex[0] }
                                    
                                    #$str_datetime + " >>> 0" + $str_node + $str_errcategory + " 0" + $str_errsubcategory + " 0" + $str_errindex + " >>> " + $record_line | Out-File -Append $ArchiveFile
                                    $str_datetime + " >>> 0" + $str_node + $str_errcategory + " 0" + $str_errsubcategory + " 0" + $str_errindex | Out-File -Append $ArchiveFile
                                }
                " ""
                if ( ( element[1] == "CONTROL_TRACO" ) and ( element[5] != "TSC" ) ):
                    print(date_time, "element[5]", element[5], "VALUE", element[7])

                " ""
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
                """

            # закрываем файл
            file.close
            #file_result.close()








    ''' функция для обработки события клика в root '''

    ''' функция для обработки события клика в папку '''

    ''' функция для обработки события single-клика в zip '''

    ''' функция создания базы данных '''







''' ==================================================================== '''
if __name__ == "__main__":
    app = QApplication([])

    win = LogAnalizer()
    win.resize(600, 400)
    win.show()

    sys.exit(app.exec())

























# --------------------------------------------------------------
# connect with DB
def fn_sql_connection():
    try:
        con = sqlite3.connect('sqlite_python.db')
        return con
    except sqlite3.Error as error:
        print(error)



# --------------------------------------------------------------
# ple_events_temp - temporary table for producing class_cod & type_cod dictionaries
# destroy, then create table 'ple_events' - new and empty
## INPUT connection with DB, start and finish times of time range
## OUTPUT table 'ple_events' and dictionaries: range_class & range_type
def fn_sql_table(directory, con, moment_start, moment_stop):

    event_lines = []
    range_class = []
    range_type = []

    try:
        f_events = [f for f in os.listdir(path=directory) if f.endswith('.PLE')]
        file_data = f_events[0]
        with open(os.path.join(directory, file_data), mode="r", encoding="utf-16") as file:
            event_lines = [[e for e in row.strip().split(";")] for row in file]
    except UnicodeError as error_unnicode:
        print(error_unnicode)
    except OSError as error_file:
        print(error_file)

    try:
        cursorObj = con.cursor()
        cursorObj.execute('drop table if exists ple_events_temp')

        query_create_table_temp = """CREATE TABLE ple_events_temp (
                                        class_cod integer,
                                        type_cod integer);"""
        cursorObj.execute(query_create_table_temp)

        query_insert_table_temp = """INSERT INTO ple_events_temp
                                            (class_cod, type_cod)
                                            VALUES (?, ?);"""
        for event_line in event_lines[27:]:
            insert_data = (event_line[2], event_line[4])
            cursorObj.execute(query_insert_table_temp, insert_data)

        range_class = cursorObj.execute("SELECT DISTINCT class_cod FROM ple_events_temp;").fetchall()
        range_type = cursorObj.execute("SELECT DISTINCT type_cod FROM ple_events_temp;").fetchall()

        cursorObj.execute('drop table if exists ple_events_temp')
        con.commit()
    except sqlite3.Error as error:
        print(error)

    try:
        cursorObj.execute('drop table if exists ple_events')
        query_create_table = "CREATE TABLE ple_events ("
        for class_cod_single in range_class:
            for type_cod_single in range_type:
                query_create_table += "event_" + str(class_cod_single[0]) + "_" + str(type_cod_single[0]) + " integer, "
        query_create_table += "moment_specific text PRIMARY KEY);"
        cursorObj.execute(query_create_table)
        query_insert_data = """INSERT INTO 'ple_events'
                                        ('moment_specific')
                                        VALUES (?);"""
        for s in range(int((moment_stop-moment_start).total_seconds())):
            cursorObj.execute(query_insert_data, (moment_start+timedelta(seconds=s),))

        con.commit()
    except sqlite3.Error as error:
        print(error)

    return(range_class, range_type)



# --------------------------------------------------------------
# write data to table by UPDATE function
## INPUT connection with DB and all data
## OUTPUT
def sql_update_event(con, moment_event, matrix_logdata, range_class, range_type):
    query_update_data = "UPDATE ple_events SET "
    c = 0
    for class_cod_single in range_class:
        t = 0
        for type_cod_single in range_type:
            if c != 0 or t != 0:
                query_update_data += ", "
            query_update_data += "event_" + str(class_cod_single[0]) + "_" + str(type_cod_single[0]) + " = " + str(matrix_logdata[c][t])
            t += 1
        c += 1
    query_update_data += " WHERE moment_specific = '" + moment_event + "';"

    try:
        cursorObj = con.cursor()
        cursorObj.execute(query_update_data)
        con.commit()
    except sqlite3.Error as error:
        print(error, query_update_data)

    #print("sql_update", moment_event)


# --------------------------------------------------------------
# header for transfer data from log to DB
#   open log-file --> event_lines[]
#   open ple_events-table --> all_moments[]
## INPUT
## OUTPUT
def fn_sql_transfer_data(con, directory, range_class, range_type):
    event_lines = []
    try:
        f_events = [f for f in os.listdir(path=directory) if f.endswith('.PLE')]
        file_data = f_events[0]
        with open(os.path.join(directory, file_data), mode="r", encoding="utf-16") as file:
            event_lines = [[e for e in row.strip().split(";")] for row in file]
    except UnicodeError as error_unnicode:
        print(error_unnicode)
    except OSError as error_file:
        print(error_file)

    all_moments = []
    try:
        cursorObj = con.cursor()
        sql_select_moment_specific = """SELECT moment_specific
                                        FROM ple_events;"""
        cursorObj.execute(sql_select_moment_specific)
        all_moments = cursorObj.fetchall()
        con.commit()
    except sqlite3.Error as error_sql:
        print(error_sql)
    moments_count = len(all_moments)

    matrix_logdata = []
    for class_cod_single in range_class:
        matrix_logdata_inner = []
        for type_cod_single in range_type:
            matrix_logdata_inner.append(0)
        matrix_logdata.append(matrix_logdata_inner)

    #start = datetime.now()

    iterator_events = iter(event_lines[27:])
    current_record = next(iterator_events)
    moment_event = current_record[1]
    class_cod =current_record[2]
    type_cod = current_record[4]
    sample_cod = current_record[6]
    previous_moment = str(0)

    for moment_record in all_moments:
        moment_record = moment_record[0]

        if moment_record >= moment_event:
            while True:
                previous_moment = moment_event
                moment_event = current_record[1]
                class_cod =current_record[2]
                type_cod = current_record[4]
                sample_cod = current_record[6]
                is_break = False
                c = 0
                for class_cod_single in range_class:
                    t = 0
                    for type_cod_single in range_type:
                        if int(class_cod_single[0]) == int(class_cod) and int(type_cod_single[0]) == int(type_cod):
                            matrix_logdata[c][t] = sample_cod
                            is_break = True
                            break
                        t += 1
                    c += 1
                    if is_break:
                        break
                try:
                    current_record = next(iterator_events)
                except StopIteration:
                    # if StopIteration is raised, break from loop
                    break
                if current_record[1] != previous_moment:
                    break

        sql_update_event(con, moment_record, matrix_logdata, range_class, range_type)

    #print(datetime.now(), "stop - ", (datetime.now() - start))





# preparation data selected
# --------------------------------------------------------------
#
## INPUT
## OUTPUT
def fn_data_prepare(data_file):
    print(data_file.name)
    # создаём временную директорию
    with tempfile.TemporaryDirectory() as directory:
        try:
            shutil.copyfile(data_file, os.path.join(directory, "log_file_packed"))
        except IOError:
            print("Copy failed")
        archive = tarfile.open(os.path.join(directory, "log_file_packed"), "r:gz")
        archive.extractall(directory)

        moment_start, moment_stop = fn_extract_start_stop_time(directory)
        moment_start = datetime.strptime(moment_start, '%Y-%m-%d %H:%M:%S')
        moment_stop = datetime.strptime(moment_stop, '%Y-%m-%d %H:%M:%S')
        #print("Duration = ", moment_stop-moment_start, " == ", (moment_stop-moment_start).total_seconds())

        #
        con = fn_sql_connection()
        #
        (range_class, range_type) = fn_sql_table(directory, con, moment_start, moment_stop)
        #
        fn_sql_transfer_data(con, directory, range_class, range_type)




















































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