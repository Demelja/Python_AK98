#!/usr/bin/python3
# -*- coding: utf-8 -*-

### Console Version

"""
There is Analizator / Visualization tool for log-files from AK98
Dmytro Melnychenko had made this.
06-JAN-2022 is the first day
"""

##-- AK98_log_analizer.txt_to_sqlite_converter.MACHINEMODE_2_up_to_3
##-- Dmytro Melnychenko AKA D-Man
##-- program name - ?




#-- libraries
import os
import sys
import tempfile
import shutil
import zipfile

import sqlite3

from datetime import datetime





## HARD CORE DATA
### 
file_data_name = 'ak98.log.txt'
file_database_name = 'AK98_full_log.db'
log_archive_name = "Archive.zip" #zip-file should be renamed
### перечень (кортеж ?) кодов параметров
range_variables = [ "650", "534", "1651", "1682", 
            "2484", "2385", "3189", "2578", "2690", "2952", "2749", "2322",
            "2122", "2123", "2141", "2142", "1891", "1894", "3537", "3869",
            "2157", "2162", "2120", "2193", "2200",
            "2119", "2073", "2116", 
            "2086", "1632", 
            "1706",
            "2184", 
            "1765", 
            "2074" ]
range_astrings = [ "TMP", 
            "UF_RATE", "UF_CHANNEL_1_FLOW", "UF_CHANNEL_2_FLOW", "UF_CHANNEL_1_FLOW_FILTERED", "UF_CHANNEL_2_FLOW_FILTERED", 
            "UF_SUPERVISION_CHANNEL_1_FLOW", "UF_SUPERVISION_CHANNEL_2_FLOW", "UF_SUPERVISION_UF_RATE",
            "UFS_UFRATE_MEASURED", "UFS_TAR_START", "UFS_BL_PUMP_ACTIVE", "UFS_FILTR_UFR", "UFS_CP_DIFF_UFR",
            "UFS_ACCUMULATED_MEASURED_UFRATE", "UFS_ACCUMULATED_IDEAL_UFRATE", 
            "PD_PRESSURE", "VENOUS_PRESSURE", "VENOUS_PRESSURE_P", "ARTERIAL_PRESSURE",
            "DIALYSIS_FLUID_PATH_FLOW_STATUS", "FLOW_SWITCH", "BLOOD_LEAK_DETECTOR_BLU", "BUBBLE_TRAP_POSITION",
            "A_TEMPERATURE", "B_TEMPERATURE", "C_TEMPERATURE", "P_TEMPERATURE", "B_TEMPERATURE_COMP",
            "HEATER_OUTLET_TEMPERATURE", "UI_IO_P_TEMPERATURE", "POWER_IO_P_TEMPERATURE",
            "A_CONDUCTIVITY", "B_CONDUCTIVITY", "P_CONDUCTIVITY",
            "A_CONCENTRATE_PUMP_SPEED_DEVIATION", "B_CONCENTRATE_PUMP_SPEED_DEVIATION",
            "SAFETY_GUARD_PRESSURE_SWITCH", 
            "PROTECTIVE_VALVE_SET_OPEN_CLOSE", "CONTROL_VALVE_SET_OPEN_CLOSE",
            "PROTECTIVE_VALVE_OPENED_CLOSED", "CONTROL_VALVE_OPENED_CLOSED", 
            "BATTERY_COND_TEST_VOLTAGE_RESULT" ]
#range_variables = [ "650", "534", "1651", "1682", "2484", "2385", "3189", "2578", "2690", "2952", "2749", "2322", "2122", "2123", "2141", "2142", "1891", "1894", "3537", "3869", "2157", "2162", "2120", "2193", "2200", "2119", "2073", "2116", "2086", "1632", "1706", "2184", "1765", "3537", "2074" ]
#range_astrings = [ "TMP", "UF_RATE", "UF_CHANNEL_1_FLOW", "UF_CHANNEL_2_FLOW", "UF_CHANNEL_1_FLOW_FILTERED", "UF_CHANNEL_2_FLOW_FILTERED", "UF_SUPERVISION_CHANNEL_1_FLOW", "UF_SUPERVISION_CHANNEL_2_FLOW", "UF_SUPERVISION_UF_RATE", "UFS_UFRATE_MEASURED", "UFS_TAR_START", "UFS_BL_PUMP_ACTIVE", "UFS_FILTR_UFR", "UFS_CP_DIFF_UFR", "PD_PRESSURE", "VENOUS_PRESSURE", "VENOUS_PRESSURE_P", "ARTERIAL_PRESSURE", "DIALYSIS_FLUID_PATH_FLOW_STATUS", "FLOW_SWITCH", "BLOOD_LEAK_DETECTOR_BLU", "BUBBLE_TRAP_POSITION", "A_TEMPERATURE", "B_TEMPERATURE", "C_TEMPERATURE", "P_TEMPERATURE", "B_TEMPERATURE_COMP", "HEATER_OUTLET_TEMPERATURE", "UI_IO_P_TEMPERATURE", "POWER_IO_P_TEMPERATURE", "A_CONDUCTIVITY", "B_CONDUCTIVITY", "P_CONDUCTIVITY", "A_CONCENTRATE_PUMP_SPEED_DEVIATION", "B_CONCENTRATE_PUMP_SPEED_DEVIATION", "SAFETY_GUARD_PRESSURE_SWITCH", "PROTECTIVE_VALVE_SET_OPEN_CLOSE", "CONTROL_VALVE_SET_OPEN_CLOSE", "PROTECTIVE_VALVE_OPENED_CLOSED", "CONTROL_VALVE_OPENED_CLOSED", "BATTERY_COND_TEST_VOLTAGE_RESULT" ]












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
            return cursorObj.execute( "select COUNT(*) from 'ak98_events'" ).fetchone()[0]

        except sqlite3.Error as error:
            print(error)


    # drop and create table
    def fn_sql_table(self, con):
        try:
            cursorObj = con.cursor()
            cursorObj.execute( "drop table if exists 'ak98_events'" )
            
            query_create_table = "CREATE TABLE 'ak98_events' ('moment_specific' TEXT PRIMARY KEY, 'technical_error' TEXT, 'machine_mode' TEXT, 'attention_message' TEXT, "
            for event_variable in range_variables:
                query_create_table += "'c" + str(event_variable) + "' TEXT, "
            for event_astring in range_astrings:
                query_create_table += "'" + str(event_astring) + "' TEXT, "
            query_create_table += "'archive_name' TEXT);"
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
            print(error, " >>> ", datatime_mark, " >>> INSERT")


    # insert data
    def fn_update_data(self, con, data):
        try:
            cursorObj = con.cursor()
            
            query_insert_data = "UPDATE ak98_events SET '"
            query_insert_data += data[0]
            query_insert_data += "' = "
            query_insert_data += data[1]
            query_insert_data += ", 'machine_mode' = "
            query_insert_data += data[3]
            query_insert_data += " WHERE moment_specific = '"
            query_insert_data += data[2] + "';"
            cursorObj.execute(query_insert_data)

            con.commit()

        except sqlite3.Error as error:
            print(error, " >>> ", data[2], " >>> UPDATE")


    # --------------------------------------------------------------
    def tech_error_number_decode(self, current_line_of_log):
        """"""
        part_of_line = (current_line_of_log.strip()).split(" ")
        
        if ( len( part_of_line[5] ) == 1 ):
            sub_node_num = "0" + part_of_line[5]
        else:
            sub_node_num = part_of_line[5]
        
        if ( len( part_of_line[7].split("=")[1] ) == 1 ):
            node_num = "0" + part_of_line[7].split("=")[1]
        else:
            node_num = part_of_line[7].split("=")[1]
        
        if ( len( part_of_line[8].split("=")[1] ) == 1 ):
            sub_cat_num = "00" + part_of_line[8].split("=")[1]
        else:
            if ( len( part_of_line[7].split("=")[1] ) == 2 ):
                sub_cat_num = "0" + part_of_line[8].split("=")[1]
            else:
                sub_cat_num = part_of_line[8].split("=")[1]
        
        if ( len( part_of_line[9].split("=")[1] ) == 1 ):
            err_num = "00" + part_of_line[9].split("=")[1]
        else:
            if ( len( part_of_line[9].split("=")[1] ) == 2 ):
                err_num = "0" + part_of_line[9].split("=")[1]
            else:
                err_num = part_of_line[9].split("=")[1]
        
        if ( len( part_of_line[10].split("=")[1] ) == 1 ):
            cat_num = "00" + part_of_line[10].split("=")[1]
        else:
            if ( len( part_of_line[10].split("=")[1] ) == 2 ):
                cat_num = "0" + part_of_line[10].split("=")[1]
            else:
                cat_num = part_of_line[10].split("=")[1]
        
        tech_error_number = sub_node_num + "" + node_num + " " + sub_cat_num + " " + err_num + " " + cat_num + " :: " + part_of_line[6].split("=")[1]
        
        return tech_error_number


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
            files.sort()
            for file in files:
                print(file.split(".")[0])
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

                    #
                    machine_mode = "-"

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
                                #date_time = (element[0].split("-"))[0]
                                date_time_formatted = date_time.split("_")[0][0:4] + "-" + date_time.split("_")[0][4:6] + "-" + date_time.split("_")[0][6:8] + " " + date_time.split("_")[1]
                                
                                # если событие происходит в тот же момент, то нет нужды создавать новую строку в базе данных
                                if ( date_time_prior != date_time ):
                                    date_time_prior = date_time
                                    self.fn_insert_new_row(sql_connection, date_time_formatted, file.split('.')[0])
                                    
                                """
                                                3.1.2. если элемент [1] равен строке "CONTROL_TRACO", записать в БД элемент [5] в соответствующий столбец, а элемент [7] - в столбец "VALUE"
                                                3.1.3. если элемент [1] равен строке "UI_CANLOG" AND элемент [3] не равен "MACHINEMODE_UI" AND элемент [4] не равен "DIAGNOSTIC_RAISED", 
                                                    записать в БД элемент [4] в соответствующий столбец, а элемент [5] - в столбец "VALUE"
                                """

                                if ( element[1] == 'UI_CANLOG' and element[4] == 'MACHINE_MODE' ):
                                    machine_mode = "" + element[5]

                                if ( element[1] == 'CONTROL_TRACO' and element[5] in range_variables ):
                                    self.fn_update_data(sql_connection, ["c"+element[5], element[7], date_time_formatted, machine_mode])

                                if ( element[1] == 'UI_CANLOG' and element[4] in range_astrings ):
                                    self.fn_update_data(sql_connection, [element[4], element[5], date_time_formatted, machine_mode])

                                if ( element[1] == 'UI_CANLOG' and element[4] == 'DIAGNOSTIC_RAISED' ):
                                    tech_error_number = "'" + self.tech_error_number_decode(line) + "'"
                                    #print("----------------------------------------------------------- ", tech_error_number)
                                    self.fn_update_data(sql_connection, ['technical_error', tech_error_number, date_time_formatted, machine_mode])

                                if ( element[1] == 'UI_CANLOG' and element[4] == 'ATTENTION_RAISED' ):
                                    attention = "'" + element[5] + " :: " + element[6].split("=")[1] + "'"
                                    self.fn_update_data(sql_connection, ['attention_message', attention, date_time_formatted, machine_mode])

                                if ( element[1] == 'UI_CANLOG' and element[4] == 'ATTENTION_P_RAISED' ):
                                    attention_p = "'" + element[5] + " :_P_: " + element[6].split("=")[1] + "'"
                                    self.fn_update_data(sql_connection, ['attention_message', attention_p, date_time_formatted, machine_mode])

                                if ( element[1] == 'UI_CANLOG' and element[4] == 'ALARM_RAISED' ):
                                    alarm = "'" + element[5] + " :: " + element[6].split("=")[1] + "'"
                                    self.fn_update_data(sql_connection, ['attention_message', alarm, date_time_formatted, machine_mode])

                                if ( element[1] == 'UI_CANLOG' and element[4] == 'ALARM_P_RAISED' ):
                                    alarm_p = "'" + element[5] + " :_P_: " + element[6].split("=")[1] + "'"
                                    self.fn_update_data(sql_connection, ['attention_message', alarm_p, date_time_formatted, machine_mode])

                        # END: if ( len( element ) > 2 )

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

    print("Total records -- ", a.fn_count_records(sql_conn))
    

print("That\'s all, folks!!!")
sys.exit()