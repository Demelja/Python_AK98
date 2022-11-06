#!/usr/bin/python3
# -*- coding: utf-8 -*-

### Console Version

##----- line_with_different_scale.py


from mpl_toolkits import mplot3d

import matplotlib.pyplot as plt
import sqlite3

conn = sqlite3.connect('AK98_log_pressure.db')
c = conn.cursor()

#c.execute('''SELECT time_since_start*1, c2122*1, c2141*1, PD_PRESSURE*1 FROM ak98_events WHERE archive_name = "Archive_4469_202208010940" AND (c2122 IS NOT NULL OR c2141 IS NOT NULL OR PD_PRESSURE IS NOT NULL);''')

#rows = c.fetchall()

time_since_start = []
pressure_1 = []
pressure_2 = []
pressure_3 = []

'''
for row in rows:
    time_since_start.append(row[0])
    pressure_1.append(row[1])
    pressure_2.append(row[2])
    pressure_3.append(row[3])
'''

#figu = plt.figure()
ax = plt.axes(projection ='3d')

c.execute('''SELECT archive_name FROM ak98_events GROUP BY archive_name;''')
rows_archive = c.fetchall()

for row in rows_archive:
	#print(row)
    q = "SELECT time_since_start*1, c2122*1, c2141*1, PD_PRESSURE*1 FROM ak98_events WHERE archive_name = '" + row[0] + "' AND (c2122 IS NOT NULL OR c2141 IS NOT NULL OR PD_PRESSURE IS NOT NULL) ORDER BY time_since_start*1 LIMIT 10;"
    c.execute(q)
    rows_pressure = c.fetchall()

    time_since_start.clear()
    pressure_1.clear()
    pressure_2.clear()
    pressure_3.clear()

    for row in rows_pressure:
        time_since_start.append(int(row[0]))
        pressure_1.append(row[1])
        pressure_2.append(row[2])
        pressure_3.append(row[3])

    #plt.scatter(time_since_start, pressure_1)
    #plt.scatter(time_since_start, pressure_2)
    plt.plot(time_since_start, pressure_3)

    #print(len(time_since_start))

    i = 0
    for time_moment in time_since_start:
        i = i + 1
        #ax.plot3D(time_since_start, pressure_3, i)
        print(i)

    ax.scatter3D(time_since_start, pressure_3, i)


#commit the changes to db			
conn.commit()
#close the connection
conn.close()




# X and Y data

numberofemp = [13, 200, 250, 300, 350, 400]

rev = [0.4, 0.6, 0.8, 0.7, 0.8, 0.9]

year = [2011, 2012, 2013, 2014, 2015, 2016]



# plot numberofemp on xaxis_1
fig, xaxis_1 = plt.subplots()

#xaxis_1.plot( year, numberofemp, marker="D", mfc="green", mec="yellow", ms="7" )
xaxis_1.plot( time_since_start, pressure_1, marker="D", mfc="green", mec="yellow", ms="7" )

xaxis_1.plot( time_since_start, pressure_2, marker="D", mfc="red", mec="yellow", ms="7" )

xaxis_1.plot( time_since_start, pressure_3, marker="D", mfc="blue", mec="yellow", ms="7" )

xaxis_1.set_xlabel("Year")

xaxis_1.set_ylabel("Number of Employees")

xaxis_1.set_title("Number of Employee and Revenue")
"""
# create xaxis_2 with shared x-axis

xaxis_2 = xaxis_1.twinx()

# plot rev on xaxis_2

xaxis_2.plot(year, rev, marker="o", mfc="red", mec="green",ms="7")

xaxis_2.set_ylabel("Rev [$M]")

# setting the legend
"""
fig.legend(["Number of Employee", "Rev"], loc="upper left")

plt.show()