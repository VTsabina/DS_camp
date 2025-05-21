#!./delmerfi/bin/python3

import pstats
from pstats import SortKey

# ./pstats_sorting.py > pstats-cumulative.txt

if __name__ == '__main__':
    p = pstats.Stats('stats')
    p.sort_stats(SortKey.CUMULATIVE).print_stats(5)
