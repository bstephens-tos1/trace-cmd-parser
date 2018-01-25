'''
Relevant information from lines of the trace-cmd report.
'''
class TraceStats:
	def __init__(self,name,d,f):
		self.tracepoint = name
		# Duration is in us
		self.total_duration = d
		self.frequency = f
		# We will update this later, as more points are gathered.  It
		# just needs a non-zero value for now
		self.avg_duration = self.total_duration/1

	'''
	This function will update an entry by increasing its frequency and total duration.
	These values can be used to calculate average duration.
	'''
	def updateStats(self, d, f):
		self.total_duration = self.total_duration + d
		self.frequency = self.frequency + f
		self.avg_duration = self.total_duration/self.frequency


'''
Used in parsing a line from trace-cmd report.  The intended usage is to have a stack of
ReportLines.  The usage is discussed in the parsing section.

format example:
trace-cmd-5540  [001]  4957.339078: funcgraph_entry:                   |  _raw_spin_lock_irqsave() {
loadgen-5545  [002]  4957.339082: funcgraph_exit:         0.688 us   |    }
trace-cmd-5540  [001]  4957.339082: funcgraph_entry:        0.054 us   |      rcu_irq_enter();

In any case, we see that the lines of interest will fill 7 slots of an array.
'''
class ReportLine:
	def __init__(self):
		self.process = ""
		self.cpu = 0
		self.timestamp = 0.0
		# Are we an entry or exit function?
		self.entry = 0
		self.duration_us = 0.0
		self.function_name = ""
		self.seq_num = 0

	'''
	Extracts a ReportLine from a given string, if possible.
	'''
	def rlFromString(self, line, event_num):
		# Lines that do not meet the length requirement cannot be parsed correctly.
		if(len(line) < 7):
			return False

		# There are some lines which meet the length requirement but are still not the lines
		# we are looking for, which take a form similar to:
		# trace-cmd-4510  [002]  3650.821403: ext4_da_write_begin:  dev 8,3 ino 3172572 pos 20480 len 4096 flags 0
		# TODO: how to properly handle these lines?
		if(line[3] == "funcgraph_entry:"):
			self.entry = 1
		#elif(line[3] == "funcgraph_exit:"):
		else:
			self.entry = 0
		#else:
		#	return False

		self.process = line[0]
		self.cpu = float(line[1].strip("[]"))
		self.timestamp = line[2].strip(":")
		self.seq_num = event_num

		# funcgraph entries that did not make any subsequent function calls have a duration
		# just like funcgraph exits.  These entries can be spotted because their trace line
		# does not end with an opening brace {.  funcgraph exits also do not end with {
		if(line[-1] != "{"):
			try:
				self.duration_us = float(line[-4])
			except ValueError as e:
				return False

		# only funcgraph entries will have a function name.  If the line ends with {, just
		# grab the second-to-last column.  Otherwise, it's the last column but it needs to have
		# a semi-colon stripped.
		if(self.entry):
			if(line[-1] == "{"):
				self.function_name = line[-2]
			else:
				self.function_name = line[-1].strip(';')

		return True

class EventMap:
	def __init__(self):
		self.tracepoint = ""
		self.event_nums = []
