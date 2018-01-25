# trace-cmd-parser
## A parsing script for trace-cmd/ftrace's func-graph output

This repo represents one of two components of my master's thesis that I am making
publicly available for portfolio reasons.  If you are reading this because I have
applied to your company, know that I am happy to show and discuss more of my
thesis work with you in person.  For anyone else, note that this code is only as
general as it needs to be for my thesis.  If you wish to modify this code at all,
please do so (but let me see your final product, as I am curious about your use case).  If you want me to add some feature or generalize the code, feel free to ask me.

parseFuncGraphReport.py is intended to parse the output of trace-cmd into an easy to handle CSV format.  This only works when trace-cmd is monitoring my workload generator, [loadgen](https://github.com/bstephens-tos1/loadgen), using the function_graph option.
For example, trace-cmd could be run as follows:

```
#: trace-cmd record -p function_graph -l ext4_* ./loadgen gen.out 4096 10 0 &> ./trace.stats
#: trace-cmd report > trace.report
```
The above commands will apply the function_graph tracer to a loadgen workload and
then generate a trace report based on the collected data. Note that everything succeeding `./loadgen` in the first line refer to parameters that are passed in to loadgen (please see the loadgen repo for more information).

Only after the above two commands have been run can you invoke parseFuncGraphReport.py,
via

```
parseFuncGraphReport.py trace.report
```

You will now have three .csv files with all of the events trace-cmd monitored in
a tidy format that can easily be imported into spreadsheet/graphing software.
