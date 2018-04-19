# trace-cmd-parser
## A parsing script for trace-cmd/ftrace's func-graph output

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
a tidy format that can easily be imported into spreadsheet/graphing software. example
output from loadgen_dur_freq.csv might look like:

```
Function Name,Frequency,Total Duration (us)
ext4_es_lookup_extent();,4,0.549
ext4_data_block_valid();,6,1.599
ext4_map_blocks(),4,11.809000000000001
ext4_getblk(),3,6.766
ext4_bread_batch(),2,5.9559999999999995
ext4_search_dir();,3,0.922
ext4_find_entry(),3,2296.009
ext4_es_init_tree();,2,0.082
ext4_alloc_inode(),2,0.963
ext4_get_group_desc();,4,0.341
ext4_inode_table();,5,0.379
ext4_itable_unused_count();,1,0.041
```

TODO: There is a known bug with this implementation that does not allow for
strip()'ing out semi-colons from function names.  This is not a problem when
consolidating with my spreadsheet software, but other users should be warned of
this.  I will look into the problem more in depth at a later date.
