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
file_database_name = 'AK98_log_pressures_and_valves_new_version.db'
#file_database_name = 'AK98_log_pressure.db'
log_archive_name = "Archive.zip" #zip-file should be renamed
### перечень (кортеж ?) кодов параметров
'''
range_variables = [ "534", "1651", "1682", 
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
'''
range_variables = [ "2122", "2141",
                    "2321", "2748", "2617", "2779", "2951", "2516", "3096", "2550", "2483", "2385", "2689", "3188", "2577", "1650", "650", "534", "1681", "1751" ]
range_astrings = [ "PD_PRESSURE", "VENOUS_PRESSURE", "VENOUS_PRESSURE_P", "ARTERIAL_PRESSURE" ]

data_variables_astrings = {}

for event_variable in range_variables:
    data_variables_astrings["c"+event_variable] = 0
for event_astring in range_astrings:
    data_variables_astrings[event_astring] = 0

#
data_variables_and_values = {}

for event_variable in range_variables:
    data_variables_and_values["c"+event_variable] = 0
for event_astring in range_astrings:
    data_variables_and_values[event_astring] = 0
data_variables_and_values['technical_error'] = ""
data_variables_and_values['attention_message'] = ""

#
flag_empty_row = True



#range_variables = [ "650", "534", "1651", "1681", "1682", "2484", "2385", "3189", "2578", "2690", "2952", "2749", "2322", "2122", "2123", "2141", "2142", "1891", "1894", "3537", "3869", "2157", "2162", "2120", "2193", "2200", "2119", "2073", "2116", "2086", "1632", "1706", "2184", "1765", "3537", "2074" ]
# F_**vaSts: AIVA-2321, REVA-2748, FLVA-2617, RIVA-2779, ZEVA-2951, DRVA-2516, CBVA-3096, (EVVA), DIVA-2483, BYVA-2384, (TAVA), CHVA-2385, INVA-2689, HBVA-3188, FIVA-2577
# F_EvvaDisOpen-2550
# FF_InValve-2085
# P_EvvaOpen-1650, O_DivaOpen-650, O_ByvaOpen-534, P_TavaOpen-1681, P_ChvaOpen-1751
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
            query_create_table += "'time_since_start' TEXT, "
            for event_variable in range_variables:
                query_create_table += "'c" + str(event_variable) + "' TEXT, "
            for event_astring in range_astrings:
                query_create_table += "'" + str(event_astring) + "' TEXT, "
            query_create_table += "'archive_name' TEXT);"
            cursorObj.execute(query_create_table)
            
            con.commit()

        except sqlite3.Error as error:
            print(error)


    # insert new row and data
    def fn_insert_new_row_and_data(self, con, datetime_mark, moment_start, log_file_name, machine_mode_current, data_variables_and_values, string_of_log):

        cursorObj = con.cursor()

        try:

            #print(datetime_mark, " -- ", moment_start)
            d1 = datetime.strptime(datetime_mark, "%Y-%m-%d %H:%M:%S")
            d2 = datetime.strptime(moment_start, "%Y-%m-%d %H:%M:%S")
            #print(d1, " === ", d2)
            diff = (d1 - d2).seconds
            #diff = "-"

            query_insert_data = "INSERT INTO 'ak98_events' ('archive_name', 'moment_specific', 'machine_mode', 'time_since_start') VALUES (?, ?, ?, ?);"
            cursorObj.execute(query_insert_data, [log_file_name, datetime_mark, machine_mode_current, diff])

            con.commit()

        except sqlite3.Error as error:
            print(error, " >>> ", datetime_mark, " >>> INSERT_Var_&_Data ", string_of_log)
        
        try:

            query_update_data = "UPDATE 'ak98_events' SET "
            for event_variable_and_value in data_variables_and_values:
                query_update_data += "'" + str(event_variable_and_value) + "' = "
                query_update_data += "'" + str(data_variables_and_values[event_variable_and_value]) + "'"
                query_update_data += ", "
            query_update_data += "'machine_mode' = '"
            query_update_data += "" + machine_mode_current + ""
            query_update_data += "' WHERE moment_specific = '"
            query_update_data += datetime_mark + "';"
            #print("UPDATE: ", query_update_data)
            cursorObj.execute(query_update_data)

            con.commit()

        except sqlite3.Error as error:
            print(error, " >>> ", datetime_mark, " >>> UPDATE_Var_&_Data ", string_of_log)


    # insert data
    def fn_update_data(self, con, data, data2):
        try:
            cursorObj = con.cursor()

            query_update_data = "UPDATE ak98_events SET "
            for event_variable in range_variables:
                query_update_data += "'c" + str(event_variable) + "' = "
                query_update_data += "'" + str(data2["c" + str(event_variable)]) + "'"
                query_update_data += ", "
            for event_astring in range_astrings:
                query_update_data += "'" + str(event_astring) + "' = "
                query_update_data += "'" + data2[event_astring] + "'"
                query_update_data += ", "
            query_update_data += "'machine_mode' = '"
            query_update_data += data[3]
            query_update_data += "' WHERE moment_specific = '"
            query_update_data += data[2] + "';"

            cursorObj.execute(query_update_data)

            con.commit()

        except sqlite3.Error as error:
            #print(error, " >>> ", data[2], " --- mach.mode = ", data[3], " >>> UPDATE")
            print(error, "UPDATE >>> ", 'query_update_data')


    # --------------------------------------------------------------
    def fn_tech_error_number_decode(self, current_line_of_log):
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

        # переменная времени ПРЕДЫДУЩЕГО события - для решения вставлять новую строку или обновить существующую
        date_time_prior = "20000101_00:00:01"
        date_time_prior_formatted = "2000-01-01 00:00:01"
        #
        date_time_start = "20000101_00:00:01"
        moment_start_formated = "2000-01-01 00:00:01"
        #
        flag_seance_start = False
        #
        flag_record_events = False
        #
        machine_mode = "-"

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

                    # получим объект файла, 'ak98.log.txt'
                    log_file = open(os.path.join(tmp_dir_logfile, file_data_name), mode="r", encoding="utf-8")
                    
                    # считываем все строки
                    content = log_file.readlines()

                    # 3. для каждой строки:
                    for line in content:

                        # разбить строку на элементы по пробелу
                        element = (line.strip()).split(" ")

                        if ( len( element ) > 1 ):

                            # начало сеанса после слов <Logging started>
                            if ( element[0] == 'Logging' and element[1] == 'started.' ):
                                
                                date_time_prior = "20000101_00:00:01"
                                for data_variable_and_value in data_variables_and_values:
                                    data_variables_and_values[data_variable_and_value] = ""
                                machine_mode = "-"
                                moment_start_formated = "2000-01-01 00:00:01"                       ############################################### не описано вычисление

                            else:

                                # 
                                date_time = (element[0].split("-"))[0].split(".")[0]

                                # определяем момент старта сеанса
                                if ( flag_seance_start == False and date_time.split("_")[0] != "20000101" ):
                                    date_time_start = date_time
                                    flag_seance_start = True
                                
                                # если предыдущее время нулевое, то присвоить предыдущему текущее
                                if ( date_time_prior == "20000101_00:00:01" ):
                                    date_time_prior = (element[0].split("-"))[0].split(".")[0]
                                
                                # если текущее == предыдущему: прочитать данные и записать в словарь
                                if ( date_time_prior == date_time ):

                                    if ( element[1] == 'CONTROL_TRACO' and element[5] in range_variables ):
                                        for event_variable in range_variables:
                                            if ( element[5] == event_variable ): data_variables_and_values["c"+element[5]] = element[7]

                                    if ( element[1] == 'UI_CANLOG' and element[4] in range_astrings ):
                                        for event_astring in range_astrings:
                                            if ( element[4] == event_astring ): data_variables_and_values[str(element[4])] = element[5]

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'DIAGNOSTIC_RAISED' ):
                                        tech_error_number = self.fn_tech_error_number_decode(line)
                                        data_variables_and_values['technical_error'] = tech_error_number

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'ATTENTION_RAISED' ):
                                        attention = element[5] + " :: " + element[6].split("=")[1]
                                        data_variables_and_values['attention_message'] = attention

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'ATTENTION_P_RAISED' ):
                                        attention_p = element[5] + " :_P_: " + element[6].split("=")[1]
                                        data_variables_and_values['attention_message'] = attention_p

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'ALARM_RAISED' ):
                                        alarm = element[5] + " :: " + element[6].split("=")[1]
                                        data_variables_and_values['attention_message'] = alarm

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'ALARM_P_RAISED' ):
                                        alarm_p = element[5] + " :_P_: " + element[6].split("=")[1]
                                        data_variables_and_values['attention_message'] = alarm_p

                                    if ( element[1] == 'UI_CANLOG' and element[3] == 'MACHINEMODE_UI' ):
                                        machine_mode = element[5]

                                # иначе + если текущее время не нулевое
                                elif ( date_time.split("_")[0] != "20000101" ):

                                    moment_start_formated = date_time_start.split("_")[0][0:4] + "-" + date_time_start.split("_")[0][4:6] + "-" + date_time_start.split("_")[0][6:8] + " " + date_time_start.split("_")[1]
                                    date_time_prior_formatted = date_time_prior.split("_")[0][0:4] + "-" + date_time_prior.split("_")[0][4:6] + "-" + date_time_prior.split("_")[0][6:8] + " " + date_time_prior.split("_")[1]
                                    if ( machine_mode == "2" ):
                                        self.fn_insert_new_row_and_data(sql_connection, date_time_prior_formatted, moment_start_formated, file.split('.')[0], machine_mode, data_variables_and_values, line)
                                    data_variables_and_values['technical_error'] = ""
                                    data_variables_and_values['attention_message'] = ""
                                    date_time_prior = date_time

                                # END IF+ELIF: date_time_prior == date_time
                            
                            # END IF+ELSE: element[0] == 'Logging' and element[1] == 'started'

                        # END IF: len( element ) > 1



































                        '''
                        if ( len( element ) > 2 ):

                            # флаг начала сеанса после слов <Logging started>
                            flag_seance_start = True

                            # determine current Machine Mode
                            # or hardkor machine_mode = '2" below
                            #if ( element[1] == 'UI_CANLOG' and element[4] == 'MACHINE_MODE' ):
                            #    machine_mode = "" + element[5]

                            if ( element[1] == 'UI_CANLOG' and element[2] == 'BLACKBOX' and element[3] == 'MACHINEMODE_UI' and element[5] == '2' and flag_record_events == False ):
                                flag_record_events = True
                                machine_mode = '2'
                                #-- то, что ниже -- оптимизировать!!!
                                date_time = (element[0].split("-"))[0].split(".")[0]
                                moment_start_formatted = date_time.split("_")[0][0:4] + "-" + date_time.split("_")[0][4:6] + "-" + date_time.split("_")[0][6:8] + " " + date_time.split("_")[1]
                            if ( element[1] == 'UI_CANLOG' and element[2] == 'BLACKBOX' and element[3] == 'MACHINEMODE_UI' and element[5] != '2' ):
                                flag_record_events = False
                            
                            if ( flag_record_events ):

                                # ---- tolerance -- 05:51:15, file size smoller -- 18 MB, 10 min.
                                date_time = (element[0].split("-"))[0].split(".")[0]
                                # ---- tolerance -- 05:15:15.345, file size much bigger -- 200 MB, 2 hrs.
                                #date_time = (element[0].split("-"))[0] 

                                #date_time_formatted = date_time.split("_")[0][0:4] + "-" + date_time.split("_")[0][4:6] + "-" + date_time.split("_")[0][6:8] + " " + date_time.split("_")[1]

                                ' ' '
                                Рассмотрим варианты:
                                1. date_time_prior < date_time -- создать новую запись в БД и 
                                                                  выгрузить в нее содержание словаря date_variables_and_values, 
                                                                  очистить значение переменных ошибок и предупреждений,
                                                                  присвоить date_time_prior = date_time
                                2. date_time_prior = date_time -- занести в словарь значения контролируемых переметров
                                3. date_time_prior > date_time and date_time == "20000101" -- очистить значение переменных ошибок и предупреждений и 
                                                                                              присвоить date_time_prior = date_time
                                ' ' '

                                # если событие происходит в НОВыЙ момент, то создать строку ПРЕДЫДУЩЕГО момента времени и выгрузить данные
                                if ( date_time_prior != date_time ):

                                    #print("2 ... ", line)
                                    date_time_prior_formatted = date_time_prior.split("_")[0][0:4] + "-" + date_time_prior.split("_")[0][4:6] + "-" + date_time_prior.split("_")[0][6:8] + " " + date_time_prior.split("_")[1]
                                    self.fn_insert_new_row_and_data(sql_connection, date_time_prior_formatted, moment_start_formatted, file.split('.')[0], machine_mode, data_variables_and_values)
                                    # очистить значение переменных ошибок и предупреждений
                                    data_variables_and_values['technical_error'] = ""
                                    data_variables_and_values['attention_message'] = ""
                                    date_time_prior = date_time

                                elif ( date_time_prior == date_time ):
                                    
                                    if ( element[1] == 'CONTROL_TRACO' and element[5] in range_variables ):
                                        for event_variable in range_variables:
                                            if ( element[5] == event_variable ):
                                                data_variables_and_values["c"+element[5]] = element[7]

                                    if ( element[1] == 'UI_CANLOG' and element[4] in range_astrings ):
                                        for event_astring in range_astrings:
                                            if ( element[4] == event_astring ):
                                                data_variables_and_values[str(element[4])] = element[5]

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'DIAGNOSTIC_RAISED' ):
                                        tech_error_number = self.fn_tech_error_number_decode(line)
                                        data_variables_and_values['technical_error'] = tech_error_number

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'ATTENTION_RAISED' ):
                                        attention = element[5] + " :: " + element[6].split("=")[1]
                                        data_variables_and_values['attention_message'] = attention

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'ATTENTION_P_RAISED' ):
                                        attention_p = element[5] + " :_P_: " + element[6].split("=")[1]
                                        data_variables_and_values['attention_message'] = attention_p

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'ALARM_RAISED' ):
                                        alarm = element[5] + " :: " + element[6].split("=")[1]
                                        data_variables_and_values['attention_message'] = alarm

                                    if ( element[1] == 'UI_CANLOG' and element[4] == 'ALARM_P_RAISED' ):
                                        alarm_p = element[5] + " :_P_: " + element[6].split("=")[1]
                                        data_variables_and_values['attention_message'] = alarm_p

                                elif ( ( date_time_prior != date_time ) and date_time.split("_")[0] == "20000101"):
                                    
                                    data_variables_and_values['technical_error'] = ""
                                    data_variables_and_values['attention_message'] = ""
                                    date_time_prior = date_time

                                # END: if ( date_time_prior != date_time ):

                        elif ( flag_seance_start ):
                            flag_seance_start = False
                            #print("flag_seance => False")
                            #self.fn_insert_new_row_and_data(sql_connection, date_time_prior_formatted, moment_start, file.split('.')[0], machine_mode, data_variables_and_values)

                        else:
                            # в этой строку мешьше двух элементов и сеанс уже закончился
                            # case: Machine_mode was not finished but the machine was shut down
                            machine_mode = '-'
                            flag_record_events = False

                        # END: if ( len( element ) > 2 )
                        '''

                    # закрываем файл
                    log_file.close



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