#!/bin/sh

(head -n 1 ../ex01/hh.csv && tail -n +2 ../ex01/hh.csv | sort -t ',' -k 2,2 -k 1,1) > hh_sorted.csv