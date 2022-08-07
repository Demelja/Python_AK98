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
            
            query_create_table = "CREATE TABLE 'ak98_events' ('archive_name' text, "
            for event_variable in range_variables:
                query_create_table += "'" + str(event_variable) + "' text, "
            for event_astring in range_astrings:
                query_create_table += "'" + str(event_astring) + "' text, "
            query_create_table += "'moment_specific' text PRIMARY KEY);"
            cursorObj.execute(query_create_table)
            
            con.commit()

        except sqlite3.Error as error:
            print(error)


    # insert new row
    def fn_insert_new_row(self, con, datatime_mark, log_file_name):
        try:
            cursorObj = con.cursor()
            
            query_insert_data = "INSERT INTO 'ak98_events' ('archive_name', 'moment_specific') VALUES (?, ?);"
            cursorObj.execute(query_insert_data, [log_file_name, datatime_mark])

            con.commit()

        except sqlite3.Error as error:
            print(error)


    # insert data
    def fn_update_data(self, con, data):
        try:
            cursorObj = con.cursor()
            
            query_insert_data = "UPDATE ak98_events SET '"
            query_insert_data += data[0]
            query_insert_data += "' = "
            query_insert_data += data[1]
            query_insert_data += " WHERE moment_specific = '"
            query_insert_data += data[2] + "';"
            cursorObj.execute(query_insert_data)

            con.commit()

        except sqlite3.Error as error:
            print(error)


    # --------------------------------------------------------------
    def fn_unpack_log_archive(self, tmp_dir, log_archive_file_name):
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

        # move down to archives of log-data files location
        tmp_dir_archive = os.path.join(tmp_dir, "eMMC2")
        tmp_dir_archive = os.path.join(tmp_dir_archive, "LogArchive")

        return tmp_dir_archive


    # --------------------------------------------------------------
    def fn_read_log_txt_to_sql(self, tmp_dir_archive, sql_connection):

        # перебор всех файлов
        for subdir, dirs, files in os.walk(tmp_dir_archive):
            for file in files:
            # unpack
                with zipfile.ZipFile(os.path.join(tmp_dir_archive, file), 'r') as archive:
                    archive.extractall(tmp_dir_archive)
                    # move down to log-data file location
                    #tmp_dir_logfile = os.path.join(tmp_dir_archive, os.path.splitext(os.path.basename(os.listdir(path=tmp_dir_archive)[0]))[0])
                    tmp_dir_logfile = os.path.join(tmp_dir_archive, "eMMC2")
                    tmp_dir_logfile = os.path.join(tmp_dir_logfile, "LogArchive")
                    tmp_dir_logfile = os.path.join(tmp_dir_logfile, file.split('.')[0])
                    tmp_dir_logfile = os.path.join(tmp_dir_logfile, "logdata")
                    tmp_dir_logfile = os.path.join(tmp_dir_logfile, "blackbox")

                    """
                    5. проверить наличие файла ak98.log.txt. Если не найден - сообщить и выйти
                    Если найден, запустить далее """

                    # получим объект файла
                    # FILE_DATA_NAME -- хардкор, 'ak98.log.txt'
                    log_file = open(os.path.join(tmp_dir_logfile, file_data_name), mode="r", encoding="utf-8")

                    # считываем все строки
                    content = log_file.readlines()

                    # переменная времени ПРЕДЫДУЩЕГО события - для решения вставлять новую строку или обновить существующую
                    date_time_prior = ""
                    flag_record_events = False

                    # 3. для каждой строки:
                    for line in content:
                        # разбить строку на элементы
                        # 3.1. разделить по пробелу
                        element = (line.strip()).split(" ")

                        if ( len( element ) > 2 ):

                            if ( element[1] == 'UI_CANLOG' and element[2] == 'BLACKBOX' and element[3] == 'MACHINEMODE_UI' and element[5] == '2' ):
                                flag_record_events = True
                            
                            if ( element[1] == 'UI_CANLOG' and element[2] == 'BLACKBOX' and element[3] == 'MACHINEMODE_UI' and element[5] == '3' ):
                                flag_record_events = False
                            
                            #print(len(content), " >>> ", len(element), " >>> ", flag_record_events)

                            if ( flag_record_events ):
                                """
                                                3.1.1. для элемента [0]: разделить по "-"
                                                        для элемента [0]: разделить по "."
                                                                        сравнить с "предыдущим" значением. Если НЕ СОВПАДАЕТ - создать новую строку в БД
                                                        для элемента [0]: преобразовать в дату и время, записать в БД
                                                        для элемента [1]: записать в БД
                                """
                                date_time = (element[0].split("-"))[0].split(".")[0]
                                
                                # если событие происходит в тот же момент, то нет нужды создавать новую строку в базе данных
                                if ( date_time_prior != date_time ):
                                    date_time_prior = date_time
                                    self.fn_insert_new_row(sql_connection, date_time, file.split('.')[0])
                                    
                                """
                                                3.1.2. если элемент [1] равен строке "CONTROL_TRACO", записать в БД элемент [5] в соответствующий столбец, а элемент [7] - в столбец "VALUE"
                                                3.1.3. если элемент [1] равен строке "UI_CANLOG" AND элемент [3] не равен "MACHINEMODE_UI" AND элемент [4] не равен "DIAGNOSTIC_RAISED", 
                                                    записать в БД элемент [4] в соответствующий столбец, а элемент [5] - в столбец "VALUE"
                                """

                                if ( element[1] == 'CONTROL_TRACO' and element[5] in range_variables ):
                                    self.fn_update_data(sql_connection, [element[5], element[7], date_time])

                                if ( element[1] == 'UI_CANLOG' and element[4] in range_astrings ):
                                    self.fn_update_data(sql_connection, [element[4], element[5], date_time])

                                count_records = self.fn_count_records(sql_connection)
                                print( count_records )
                        
                        # END: if ( len( element ) > 0 )

                    # закрываем файл
                    log_file.close
                    #file_result.close()













































# ====================================================================
# ====================================================================
# for future: start from command line with parameters
if len (sys.argv) > 1:
    print ("Attached, {}!".format (sys.argv[1] ) )
else:
    print ("Nothing attached, execute file only")





# create temporary directory -> analize -> remove temp.directory
with tempfile.TemporaryDirectory() as directory:

    a = LogAnalizer()

    # прочитать из командной строки второй параметр
    #__log_archive = "" 

    # выпаковать целевой файл архива событий
    t_dir = a.fn_unpack_log_archive(directory, log_archive_name)

    # 1. create database file
    sql_conn = a.fn_sql_connection()
    
    # 2.
    a.fn_sql_table(sql_conn)

    # 3.
    a.fn_read_log_txt_to_sql(t_dir, sql_conn)

    # (range_class, range_type) = fn_sql_table(tmp_dir, con, moment_start, moment_stop)
    #
    # fn_sql_transfer_data(con, tmp_dir, range_class, range_type)
    

print("That\'s all, folks!!!")
sys.exit()