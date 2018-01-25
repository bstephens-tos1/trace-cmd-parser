#!/usr/bin/python3

import sys
import os
import argparse
import tracestats as ts
import tracedict as td


LOADGEN_EVENT_FILE = "loadgen_events.csv"
LOADGEN_STATS_FILE = "loadgen_dur_freq.csv"
TRACECMD_EVENT_FILE = "tracecmd_events.csv"

###################################
#
#	FILE/ARG HANDLING
#
###################################

p = argparse.ArgumentParser(description="Parse trace-cmd output.")
p.add_argument("trace", type=str, help="The trace file to be parsed.")
args = p.parse_args()

# Python will terminate if this does not succeed; no need to check if the file was opened
f = open(args.trace, 'r')
lines = [line.strip().split() for line in f]
f.close()

###################################
#
#	TRACE PARSING
#
###################################

'''
Adds a parsed instance of ReportLine to an event dictionary
'''
def addToEventDict(reportLine, dictionary):
	# If the function_name has already been added, just append it
	if reportLine.function_name in dictionary.keys():
		dictionary[reportLine.function_name].event_nums.append(reportLine.seq_num)
	# Otherwise, create it
	else:
		events = ts.EventMap()
		events.tracepoint = reportLine.function_name
		events.event_nums.append(reportLine.seq_num)
		dictionary[reportLine.function_name] = events

'''
Adds a parsed instance of ReportLine to a tracestat dictionary
'''
def addToStatsDict(reportLine, dictionary):
	# If the function_name has already been added, just update it
	if reportLine.function_name in dictionary.keys():
		dictionary[reportLine.function_name].updateStats(reportLine.duration_us, 1)
	# Otherwise, create it
	else:
		stats = ts.TraceStats(reportLine.function_name,reportLine.duration_us,1)
		dictionary[reportLine.function_name] = stats

# These dictionaries will hold one of each tracepoint all sequence numbers which
# they occurred at
loadgenEvents = {}
tracecmdEvents = {}

# This dictionary will hold instances of tracestats, keeping track of the
# frequency and duration per function
loadgenStats = {}

# event_count keeps track of the sequence of events
# nontrace_count keeps track of the # of events that are not being traced
traced_event_count = 0
nontraced_event_count = 0

loadgen_event_count = 0
tracecmd_event_count = 0

reportStack = []

'''
########################################## MAIN TRACE REPORT PROCESSING
##########################################
'''
for line in lines:
	# Anything line with less than 7 tokens will not have data that we need
	# TODO: What about the information on the lines that are not handled?
	if(len(line) < 7):
		continue

	reportLine = ts.ReportLine()

	# There are some lines which meet the length requirement but are still not the lines
	# we are looking for, which take a form similar to:
	# trace-cmd-4510  [002]  3650.821403: ext4_da_write_begin:  dev 8,3 ino 3172572 pos 20480 len 4096 flags 0
	# TODO: how to properly handle these lines?
	if(line[3] == "funcgraph_entry:"):
		reportLine.entry = 1
	#elif(line[3] == "funcgraph_exit:"):
	else:
		reportLine.entry = 0
	#else:
	#	return False
	#
	reportLine.process = line[0]
	# This variable is used to determine what our calling process is. Having this
	# variable and comparing it to "trace" or "loadgen" is faster than using
	# a regular expression search, which is useful with huge amounts of data

	p_helper = reportLine.process.split('-')[0]

	# If we have a funcgraph_exit, first try to pop it off.  Be weary of
	# poping from an empty stack.
	if not reportLine.entry:
		try:
			reportLine = reportStack.pop()
		except IndexError as e:
			continue

		# We consider funcgraph_exits as non-traced events, since *something*
		# is happening from the tracecmd perspective.
		# TODO: check to see if the event has a calling process of trace-cmd?
		# Maybe not needed, as long as we understand traced events apply to
		# funcgraph_entries only
		nontraced_event_count = nontraced_event_count + 1

	# If we have an opening bracket, then we need to pop on to our stack
	# because these lines do not have durations on them
	# TODO: remove semi-colon from function names.  .strip(';') doesn't seem
	# to be working
	elif(line[-1] == "{"):
			reportLine.function_name = line[-2]
			reportStack.append(reportLine)
	# It wasn't a funcgraph_exit and it didn't end with an opening bracket {,
	# so it must be a funcgraph_entry with a duration on it.  The function_names
	# on these lines are in a different location than other funcgraph_entries
	else:
		reportLine.function_name = line[-1]

	# funcgraph entries that did not make any subsequent function calls have a
	# duration just like funcgraph exits.  These entries can be spotted because
	# their trace line does not end with an opening brace {.  funcgraph exits
	# also do not end with {
	if(line[-1] != "{"):
		try:
			reportLine.duration_us = float(line[-4])
		except ValueError as e:
			continue

		if (p_helper == "loadgen"):
			addToStatsDict(reportLine, loadgenStats)

	'''
	Just to help clean up the if statements immediately below
	'''
	def isBeingTraced(s):
		if(s == "loadgen" or s == "trace"):
			return True
		return False

	if reportLine.entry and isBeingTraced(p_helper):
		traced_event_count = traced_event_count + 1
		reportLine.seq_num = traced_event_count

		if(p_helper == "loadgen"):
			addToEventDict(reportLine, loadgenEvents)
			loadgen_event_count = loadgen_event_count + 1
		else:
			addToEventDict(reportLine, tracecmdEvents)
			tracecmd_event_count = tracecmd_event_count + 1
	else:
		nontraced_event_count = nontraced_event_count + 1

'''
########################################## OUTFILE PREP
##########################################
'''
lg_events = []
for name,eventMap in loadgenEvents.items():
	for e in eventMap.event_nums:
		event = (name, e)
		lg_events.append(event)

tc_events = []
for name,eventMap in tracecmdEvents.items():
	for e in eventMap.event_nums:
		event = (name, e)
		tc_events.append(event)

'''
########################################## OUTFILE HANDLING
##########################################
'''

td.writeEventCSV(TRACECMD_EVENT_FILE, tc_events)
td.writeEventCSV(LOADGEN_EVENT_FILE, lg_events)
td.writeStatsCSV(LOADGEN_STATS_FILE, loadgenStats)

# trace.stats must exist by this point due to our run script
with open('trace.stats', 'a') as f:
	# Some extra stats about the trace
	numpoints = traced_event_count + nontraced_event_count
	f.write("Number of points in total: " + str(numpoints) + " ("
		+ str(nontraced_event_count) + " from non traced events, "
		+ str(loadgen_event_count) + " from loadgen, "
		+ str(tracecmd_event_count) + " from trace-cmd)\n")

	if(traced_event_count != loadgen_event_count + tracecmd_event_count):
		f.write("Panic, because traced event count is: " + str(traced_event_count)
				+ ", but that doesn't add up to lg+tc\n")
