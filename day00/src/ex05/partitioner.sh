#!/bin/sh

INPUT="../ex03/hh_positions.csv"

cat $INPUT | awk -F '\",\"|T' 'NR==1 {header=$0; next} {filename=$2".csv"} !($2 in datelist) {datelist[$2]; print header > filename} {print >> filename}'