import tracestats as ts
import os.path

def writeTimeDict(fname, tp):
	with open(fname, 'w') as f:
		for point,stamps in tp.items():
			d_line = point + ":"
			f.write(d_line)
			for s in stamps.timestamps:
				f.write(s + ",")
			f.write("\n")

def writeEventDict(fname, tp):
	with open(fname, 'w') as f:
		for point,stamps in tp.items():
			d_line = point + ":"
			f.write(d_line)
			for s in stamps.event_nums:
				f.write(str(s) + ",")
			f.write("\n")

'''
We want to append here because this information is relevant across multiple runs
within the same experiment.
'''
def writeStatsCSV(fname, ts):
	# If the file doesn't already exist, write in this header info.  We are
	# closing and reopening to append at most once per experiment, because the
	# file can only not exist at most once per experiment
	if not os.path.isfile(fname):
		with open(fname, 'w') as f:
			f.write("Function Name,Frequency,Total Duration (us)\n")
	with open(fname, 'a') as f:
		for point,stats in ts.items():
			f.write(point + "," + str(stats.frequency) + "," + str(stats.total_duration) + "\n")

'''
Sequence numbers are only relevant to the current run in an experiment.
Therefore, we do not want to append to event .csv's
'''
def writeEventCSV(fname, te):
	if not os.path.isfile(fname):
		with open(fname, 'w') as f:
			f.write("Function Name,Event Num\n")
			for e in te:
				f.write(str(e[0]) + "," + str(e[1]) + "\n")
'''
Writes to a file information about which experiment was done and which data
will be plotted.
@exp	-	experiment filename, ends with .report
@dest	-	destination file path
'''
def writeGraphText(exp, dest):
	with open(dest, 'w') as f:
		f.write(exp + "\n")
		f.write("loadgen\n")
		f.write("trace-cmd\n")

def readGraphText(fname):
	exp = ""
	with open(fname, 'r') as f:
		read_data = f.read()
		exp = read_data.split()[0]

	return exp
