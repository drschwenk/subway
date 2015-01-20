__author__ = 'schwenk'

import csv
import dateutil
import dateutil.parser
import pylab
import numpy as np
from collections import defaultdict, Counter
import pylab
import numpy as np
import matplotlib.pyplot as plt


def read_mta_file(filename):
	''' Reads mta data files formatted post 10/18/14
		The data is stored in a dictionary with
		key:  (C/A, UNIT, SCP, STATION)
		value: [[LINENAME,DIVISION,DATE,TIME,DESC,ENTRIES,EXITS].... timeseries in 4 hour blocks]
	'''
	print "\nloading " + str(filename) + "\n"
	mtaData = defaultdict(list) # This dictionary will contain the raw mta data

	try:
		with open(filename,'r') as inf:
			reader = csv.reader(inf)
			next(reader)                # skips the first line to avoid headers
			for line in reader:
				line[-1] = line[-1].strip()     #strip whitespace from last entry
				ca, unit, scpm, station = line[0:4]
				rawts = [dateutil.parser.parse(line[6]+" " +line[7]),line[9]]
				mtaData[(ca, unit, scpm, station)].append(rawts)
		return mtaData
	except IOError:
		print "File not found"
		return 1

def makedaily_ts(rawts):
	''' Creates a total daily count per turnstile in the mta data. Among many caveats in the data are count resets.
	The core of the function builds a list representing a daily time series for each turnstile. When a new day is
	detected, the counts at the beginning and end of the previous day are used to compute the daily total.
	When a reset occurs, the end of day count will not be larger, and the logic fails. When this happens, the time
	series is inspected and the reset time time is found. The total counts on either side of the reset are summed and
	used as the daily count.
	'''

	print "calculating daily total entries for " + str(len(rawts.keys())) + " turnstiles\n"
	cperturn = defaultdict(list)  # This dictionary will contain a daily timeseries per turnstile

	for turns,times in rawts.iteritems():

		curdate = times[0][0].date()
		dailyts=[]

		for times in times:
			date = times[0].date()
			if date == curdate:
				dailyts.append(times[1])
			else:
				if int(dailyts[-1])  >=  int(dailyts[0]):
					dailycount = int(dailyts[-1]) - int(dailyts[0])
				else:                                    # A reset has occured on this day
					for h1,h2 in zip(dailyts,dailyts[1:]):
						if h2<h1:                        # reset occured between h1 and h2
							dailycount = int(dailyts[-1]) - int(h2) + int(h1) - int(dailyts[0])

				dailycount = [curdate,dailycount]
				cperturn[turns].append(dailycount)
				curdate = date
				dailyts = [times[1]]

		dailycount = int(dailyts[-1]) - int(dailyts[0])
		dailycount = [curdate,dailycount]
		cperturn[turns].append(dailycount)

	return cperturn

def collapse_scp(tsperturn):
	print "combining entry counts for " + str(len(tsperturn.keys())) + " turnstiles\n"

	unit_ts = defaultdict(dict)
	unit_ts_list = defaultdict(list)

	for turn, times in tsperturn.iteritems():
		unit = (turn[0],turn[1],turn[3])
		counts_per_date={time[0]: time[1] for time in times}
		if unit not in unit_ts.keys():
			unit_ts[unit]=counts_per_date
		else:
			for time in times:
				try:
					unit_ts[unit][time[0]]+=time[1]
				except KeyError:
					pass

	for unit,ts in unit_ts.iteritems():
		daycount = []
		# print unit, ts
		for day,count in ts.iteritems():
			daycount.append([day,count])
		unit_ts_list[unit]=daycount

	return unit_ts_list

def collapse_station(perunit):
	print "combining unit counts for " + str(len(perunit.keys())) + "  control units\n"
	perStation = defaultdict(dict)
	perStation_list=defaultdict(list)

	for unit, times in perunit.iteritems():
		station = (unit[2])
		counts_per_date={time[0]: time[1] for time in times}
		if station not in perStation.keys():

			perStation[station]=counts_per_date
		else:
			for time in times:
				perStation[station][time[0]]+=time[1]

	for station,ts in perStation.iteritems():
		daycount = []
		for day,count in ts.iteritems():
			daycount.append([day,count])
		perStation_list[station]=sorted(daycount)
	return perStation_list

def makeWeekly(stationTotals):
	print "making weekly totals for " + str(len(stationTotals.keys())) + " stations\n"
	weekly_counts = {}
	day_offset = 5     #Mta data starts on saturday, not monday.
	for station,ts in stationTotals.iteritems():
		week=[[] for i in range(7)]
		for day in ts:
			week[day[0].weekday()-day_offset]=day[1]
		weekly_counts[station]=week
	return weekly_counts


def combineWeeklyTotals(week_series):
	print "making combined timeseries for  " + str(len(week_series.keys())) + " weeks\n"
	station_total={}
	for week in week_series:
		for station, day in week.iteritems():
			if station not in station_total:
				station_total[station]=day
			else:
				station_total[station]=map(add,station_total[station],day)

	return station_total


def processing_seq(week_series):
    rawfile = read_mta_file(week_series)
    ts_pert = makedaily_ts(rawfile)
    ts_perunit = collapse_scp(ts_pert)
    ts_perStation = collapse_station(ts_perunit)
    weekly_ts = makeWeekly(ts_perStation)
    return weekly_ts
