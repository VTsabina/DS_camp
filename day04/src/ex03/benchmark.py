#!../delmerfi/bin/python3

import timeit
import sys
from functools import reduce


def loop_example(num):
    sum = 0
    for i in range(1, num + 1):
        sum += i * i
    return sum


def reduce_example(num):
    sum = reduce(lambda x, y: x + y * y, range(1, num + 1))
    return sum


if __name__ == '__main__':
    if len(sys.argv) == 4:
        try:
            sys.argv[1] += '_example'
            time = timeit.timeit(f'{sys.argv[1]}({sys.argv[3]})',
                                 globals=globals(), number=int(sys.argv[2]))
            print(f'{time:.7f}')
        except:
            print("Wrong argument: incorrect command, number of calls or integer")
