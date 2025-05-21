#!/bin/sh

OUTPUT="hh_positions.csv"

header="\"id\",\"created_at\",\"name\",\"has_test\",\"alternate_url\""
echo $header > $OUTPUT
cat *.csv | sed "/$header/d" >> $OUTPUT