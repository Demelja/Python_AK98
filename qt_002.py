#!/usr/bin/python3
# -*- coding: utf-8 -*-

### Console Version

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
import tempfile
import shutil
import zipfile

import sqlite3



## HARD CORE DATA
### 
file_data_name = 'ak98.log.txt'
file_database_name = 'AK98_full_log.db'
log_archive_name = "Archive.zip"
### перечень (кортеж ?) кодов параметров
range_variables = ["3537", "2074"]
range_astrings = ["TMP", "UF_RATE", "PD_PRESSURE"]










class LogAnalizer:
    def __init__(self, parent=None):
        self.log_archive_name = ""

    # connect with DB
    def fn_sql_connection(self):
        try:
            #print("Выполнено fn_sql_connection - перед")
            #return sqlite3.connect('AK98_full_log.db') # con = sqlite3.connect(':memory:')
            return sqlite3.connect(file_database_name) # con = sqlite3.connect(':memory:')
        except sqlite3.Error as error:
            print(error)

    #
    def fn_count_records(self, con):
        try:
            cursorObj = con.cursor()
            return cursorObj.execute( "select COUNT(*) from 'ak98_events'" )
        except sqlite3.Error as error:
            print(error)


    # drop and create table
    def fn_sql_table(self, con):
        try:
            cursorObj = con.cursor()
            cursorObj.execute( "drop table if exists 'ak98_events'" )
            
            query_create_table = "CREATE TABLE 'ak98_events' ("
            for event_variable in range_variables:
                query_create_table += "'col" + str(event_variable) + "' text, "
            for event_astring in range_astrings:
                query_create_table += "'col" + str(event_astring) + "' text, "
            query_create_table += "moment_specific text PRIMARY KEY);"
            cursorObj.execute(query_create_table)
            
            con.commit()

        except sqlite3.Error as error:
            print(error)


    # insert new row
    def fn_insert_new_row(self, con, datatime_mark):
        try:
            cursorObj = con.cursor()
            
            query_insert_data = "INSERT INTO 'ak98_events' ('moment_specific') VALUES (?);"
            cursorObj.execute(query_insert_data, [datatime_mark])

            con.commit()

        except sqlite3.Error as error:
            print(error)


    # insert data
    def fn_insert_data(self, con, data):
        try:
            cursorObj = con.cursor()
            
            query_insert_data = "UPDATE ak98_events SET col"
            query_insert_data += data[0]
            query_insert_data += " = "
            query_insert_data += data[1]
            query_insert_data += " WHERE moment_specific = '"
            query_insert_data += data[2] + "';"
            cursorObj.execute(query_insert_data)

            con.commit()

        except sqlite3.Error as error:
            print(error)


    # --------------------------------------------------------------
    def fn_create_tmp_directory(self, tmp_dir, log_archive_file_name):
        """ 1. проверка - является ли кликнутое файлом и архивом, причем не более 1 МБ размером
               - если нет, сообщить "не архив" или "это архив архивов, распакуйте сначала"
               - если да, запустить далее """

        # copy to temporary directory
        try:
            shutil.copyfile(os.path.join(os.path.dirname(__file__), log_archive_file_name), os.path.join(tmp_dir, "log_file_packed"))
        except IOError:
            print("Copy failed... ")
        else:
            print("Copied! ", str(os.path.join(tmp_dir, "log_file_packed")))
        # unpack
        with zipfile.ZipFile(os.path.join(tmp_dir, "log_file_packed"), 'r') as archive:
            archive.extractall(tmp_dir)

        # move down to log-data file location
        tmp_dir = os.path.join(tmp_dir, "eMMC2")
        tmp_dir = os.path.join(tmp_dir, "LogArchive")
        tmp_dir = os.path.join(tmp_dir, os.path.splitext(os.path.basename(os.listdir(path=tmp_dir)[0]))[0])
        tmp_dir = os.path.join(tmp_dir, "logdata")
        tmp_dir = os.path.join(tmp_dir, "blackbox")
        """
                    5. проверить наличие файла ak98.log.txt. Если не найден - сообщить и выйти
                    Если найден, запустить далее """
        return tmp_dir


    # --------------------------------------------------------------
    def fn_read_log_txt_to_sql(self, tmp_dir, sql_connection):
        # получим объект файла
        # !!!!! os.path.join(tmp_dir, __file_data) - doesn't working at all !!!!!
        #file = open(os.path.join(tmp_dir, "ak98.log.txt"), mode="r", encoding="utf-8")
        file = open(os.path.join(tmp_dir, file_data_name), mode="r", encoding="utf-8")
            
        # считываем все строки
        content = file.readlines()

        # поиск вхождений искомого текста в строке
        date_time_prior = ""

        # 3. для каждой строки:
        for line in content:
            # разбить строку на элементы
            # 3.1. разделить по пробелу
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
                #print(element[0], date_time, (element[0].split("-"))[0].split(".")[1])
                date_time_prior = date_time
                self.fn_insert_new_row(sql_connection, date_time)
            #else:
                #print("+++       ", date_time)
                
            """
                            3.1.2. если элемент [1] равен строке "CONTROL_TRACO", записать в БД элемент [5] в соответствующий столбец, а элемент [7] - в столбец "VALUE"
                            3.1.3. если элемент [1] равен строке "UI_CANLOG" AND элемент [3] не равен "MACHINEMODE_UI" AND элемент [4] не равен "DIAGNOSTIC_RAISED", 
                                записать в БД элемент [4] в соответствующий столбец, а элемент [5] - в столбец "VALUE"
            """

            if ( element[1] == 'CONTROL_TRACO' and element[5] in range_variables ):
                self.fn_insert_data(sql_connection, [element[5], element[7], date_time])

            if ( element[1] == 'UI_CANLOG' and element[4] in range_astrings ):
                self.fn_insert_data(sql_connection, [element[4], element[5], date_time])

            count_records = self.fn_count_records(sql_connection)
            print( count_records )


            # закрываем файл
        file.close
            #file_result.close()













































''' ==================================================================== '''
''' ==================================================================== '''

if len (sys.argv) > 1:
    print ("Привет, {}!".format (sys.argv[1] ) )
else:
    print ("Привет, мир!")

# создаём временную директорию
with tempfile.TemporaryDirectory() as directory:
    print('Создана >>>>>>>>>>>>> временная директория %s' % directory)

    a = LogAnalizer()

    # прочитать из командной строки второй параметр
    #__log_archive = "" 

    # выполнить преобразование в базу
    t_dir = a.fn_create_tmp_directory(directory, log_archive_name)

    # 1. создать файл базы данных
    sql_conn = a.fn_sql_connection()

    #print(sql_conn)

    # 2.
    a.fn_sql_table(sql_conn)

    # 3.
    a.fn_read_log_txt_to_sql(t_dir, sql_conn)

    # (range_class, range_type) = fn_sql_table(tmp_dir, con, moment_start, moment_stop)
    #
    # fn_sql_transfer_data(con, tmp_dir, range_class, range_type)
    

print("Финальное сообщение")
sys.exit()