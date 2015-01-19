__author__ = 'schwenk'

import csv
import dateutil
import dateutil.parser
import pylab
import numpy as np
from collections import defaultdict, Counter


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
				rawts = [[dateutil.parser.parse(line[6]+" " +line[7]),line[9]]]
				mtaData[(ca, unit, scpm, station)].extend(rawts)
		return mtaData
	except IOError:
		print "File not found"
		return 1

def makedaily_ts(rawts):
	print "calculating turnstile counts for " + str(len(rawts.keys())) + " turnstiles\n"

	cperturn = defaultdict(list)  # This dictionary will contain a daily timeseries per turnstile

	for turns,times in rawts.iteritems():
		# curdate = 5
		curdate = times[0][0].date()
		# print curdateobj
		# cperturn[turns]= []
		dailyts=[]



		for times in times:
			date = times[0].date()
			if date == curdate:
				dailyts.append(times[1])
				# print dailyts
			else:
				dailycount =int(dailyts[-1]) - int(dailyts[0])

				if dailycount > 0:
					pass
				else:
					dailycount = 0

				dailycount = [curdate,dailycount]
				cperturn[turns].extend(dailycount)
				curdate = date
				dailyts = [times[1]]



				# 	ridercount =0
				# dailyts=[times[1]]
				# cperturn[turns].append([curdateobj,ridercount])
				# curdate = times[0].date().weekday()
				# curdateobj = times[0].date()
		# ridercount= int(dailyts[-1]) - int(dailyts[0])
		# curdateobj = times[0].date()
		# cperturn[turns].append([curdateobj,ridercount])
	return cperturn




################# testing with short file

# set filename manually for testing, remove later
filename = "./mta_data/short.txt"
# filename = "./mta_data/mta11.txt"
rawfile = read_mta_file(filename)
ts_perturn = makedaily_ts(rawfile)
for k,v in ts_perturn.iteritems():
	print k,v













#attempt to use numpy array
# def makedaily_ts(rawts):
# 	print "calculating turnstile counts for " + str(len(rawts.keys())) + " turnstiles\n"
# 	cperturn = defaultdict(list)  # This dictionary will contain a daily timeseries per turnstile
#
# 	for turn, hts in rawts.iteritems():
# 		hts = np.array(hts).reshape(len(hts),7)
# 		days = sorted(list(set(hts[:,2])))
#
# 		curday = 0
# 		for day in days:
# 			print hts[day][0]
#
# 	return cperturn
