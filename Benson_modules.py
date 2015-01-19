__author__ = 'schwenk'

import csv
import dateutil
import dateutil.parser
import pylab
from collections import defaultdict





def read_mta_file(filename):
	''' Reads mta data files formatted post 10/18/14
		The data is stored in a dictionary with
		key:  (C/A, UNIT, SCP, STATION)
		value: [[LINENAME,DIVISION,DATE,TIME,DESC,ENTRIES,EXITS].... timeseries in 4 hour blocks]
	'''
	print "loading " + str(filename)
	mtaData = defaultdict(list) # This dictionary will contain the raw mta data

	try:
		with open(filename,'r') as inf:
			reader = csv.reader(inf)
			next(reader)                # Skips the first line to avoid headers
			for line in reader:
				line[-1] = line[-1].strip()
				ca, unit, scpm, station = line[0:4]
				rawts = [line[4:]]
				mtaData[(ca, unit, scpm, station)].extend(rawts)
		return mtaData
	except IOError:
		print "File not found"
		return 1

def makedaily_ts(rawts):




################# testing with short file

# set filename manually for testing, remove later
filename = "./mta_data/short.txt"
rawfile = read_mta_file(filename)
