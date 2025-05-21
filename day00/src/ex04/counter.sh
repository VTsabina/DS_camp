#!/bin/sh

INPUT="../ex03/hh_positions.csv"
OUTPUT="hh_uniq_positions.csv"

echo "\""name"\"" , "\""count"\"" > $OUTPUT

tail -n +2 $INPUT | awk -F ',' '{print $3}' | sed '/'-'/d' | sort | uniq -c | awk '{print $2, $1}' OFS=',' >> $OUTPUT