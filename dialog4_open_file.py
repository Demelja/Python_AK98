#!/usr/bin/env python3
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
import threading
##from tkinter import *
import time
from tkinter import Text
#from tkinter import Label
#from tkinter import Button
from tkinter import scrolledtext
#from tkinter import Scrollbar
#from tkFont import Font
#import tkFileDialog
import tempfile
import shutil
import tarfile
import sqlite3

from tkinter import Tk, LEFT, RIGHT, TOP, X, BOTH, RAISED, Y
from tkinter import filedialog, PhotoImage
from tkinter.constants import FLAT
from tkinter.ttk import Frame, Label, Button, Style

from datetime import datetime, timedelta






# --------------------------------------------------------------
# open file explorer window
def fn_show_explorer():
    frm_left.destroy()
    frm_right.destroy()
    frm_middle.destroy()

    frm_list = Frame(root).grid(column=0, row=0)

    file_name = filedialog.askopenfilename(filetypes = (("Archive files","*.LOX"),("all files","*.*")))
    dir_name = os.path.abspath(file_name+"/..")

    lbl = Label(frm_list, text="088-88-8888, 88:880")
    lbl_width = lbl.winfo_reqwidth()
    root.update()
    root_width = root.winfo_width()
    lbl_columns = root_width // lbl_width
    rowu = 1
    colu = 1
    root.title("Zabieg się skończył:")

    with os.scandir(dir_name) as listOfEntries:
        for entry in listOfEntries:
            # печать всех записей, являющихся файлами
            if entry.is_file():
                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(entry)
                lbl2 = Button(frm_list, text=time.strftime("%Y-%m-%d, %H:%M", time.localtime(mtime))+"\r"+str(entry.name)+"\r"+str(size))
                lbl2.bind('<Button-1>', lambda event, entry=entry: fn_data_prepare(entry))
                lbl2.grid(column=colu, row=rowu, padx=4, pady=3)
                colu=colu+1
                if colu>lbl_columns:
                    colu=1
                    rowu=rowu+1
    listOfEntries.close()



# --------------------------------------------------------------
# extract data from log of events
## INPUT  "directory" - temporary directory where files unpacked/extracted
## OUTPUT momemt_start, moment_stop - tuple
def fn_extract_start_stop_time(directory):
    f_events = [f for f in os.listdir(path=directory) if f.endswith('.PLE')]
    file_data = f_events[0]
    # получим объект файла
    file = open(os.path.join(directory, file_data), mode="r", encoding="utf-16")
    i=1
    moment_start = ""
    moment_stop = ""
    while True:
        # считываем строку
        line = file.readline()
        if i==28:
            line_split = line.strip().split(";")
            moment_start = line_split[1]
        i+=1
        # прерываем цикл, если строка пустая
        if not line:
            line_split = line_upper.strip().split(";")
            moment_stop = line_split[1]
            break
        line_upper = line
    # закрываем файл
    file.close
    return moment_start, moment_stop



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



















root = Tk()
root.title("Analizator zapisów zdarzeń i działań")

w = int(root.winfo_screenwidth() // 2)
h = int(root.winfo_screenheight() // 2)
x = int(root.winfo_screenwidth() // 4)
y = int(root.winfo_screenheight() // 4)
root.geometry('{}x{}+{}+{}'.format(w, h, x, y))

root_width = root.winfo_width()
root.columnconfigure(0, weight=1, minsize=75)
root.columnconfigure(1, weight=3, minsize=200)
root.columnconfigure(2, weight=1, minsize=75)

frm_left = Frame(master=root, relief=RAISED, borderwidth=1)
frm_middle = Frame(master=root, relief=FLAT, borderwidth=1)
frm_right = Frame(master=root, relief=RAISED, borderwidth=1)

frm_left.grid(row=0, column=0, padx=8, pady=8)
frm_middle.grid(row=0, column=1, pady=8)
frm_right.grid(row=0, column=2, padx=8, pady=8)

img_prismax = PhotoImage(file=os.path.abspath(__file__+"/..")+"/prismax300.png")
btn_prismax = Button(frm_left, command=fn_show_explorer, image=img_prismax)
btn_prismax.pack(expand = True, fill = BOTH)

txt_declaration = Text(frm_middle)
txt_declaration.insert(1.0, "Clicking on the file name starts processes:\n    - check if a working directory exist. If not - create (root - \home or /User)\n    - remove any files inside a working directory\n    - un-pack the file of archive pointed to the working directory\n   - open the file named 'file.PLE', extract time-of-start and time-of-end information, calculate treatment duration\n   - re-draw the file list: scroll the row selected at the top of program window, expand this row, make file name font size bigger, show additional information, change color of row background")
txt_declaration.pack(expand = True, fill = BOTH)

img_prismaflex = PhotoImage(file=os.path.abspath(__file__+"/..")+"/prismaflex300.png")
btn_prismaflex = Button(frm_right, command=fn_show_explorer, image=img_prismaflex)
btn_prismaflex.pack(expand = True, fill = BOTH)

root.mainloop()


#-- конец - делу венец
