#!/bin/bash

set -euo pipefail

trap atexit INT

# plot generates a configuration file and a plot corresponding $logfile.
plot() {
    cat >"$pltfile" <<EOL
set term png small size 800,600
set output "$imgfile"

set ylabel "%CPU"
set y2label "%MEM"

set ytics nomirror
set y2tics nomirror in

plot "data.log" using 1 with lines axes x1y1 title "%MEM", \
     "data.log" using 2 with lines axes x1y2 title "%CPU"
EOL

    gnuplot "$pltfile"
}

# collect retrieves the data for memory footprint and CPU usage of processes.
# args: comma-separated process pid list
collect() {
    rm -f $logfile
    while true; do
        # NOTE: along with the argument PIDs (for client and server), we also
        # retrieve all the PIDs corresponding to rabbitmq user's processes.
        ps -u rabbitmq -p "$@" -o pmem=,pcpu= | awk '{s+=$1; t+=$2} END {print s " " t}' >> $logfile
        sleep 1
    done
}

atexit() {
    plot
    xdg-open "$imgfile"
    rm -f "$pltfile"
}

logfile="data.log"
pltfile=$(mktemp)
imgfile="mem-graph.png"
serverPID=$(pgrep -f 'server.py')
clientPID=$(pgrep -f 'client.py' | tr '\n' ',' | sed 's/.$//')  # trailing ','

collect "$serverPID","$clientPID"
