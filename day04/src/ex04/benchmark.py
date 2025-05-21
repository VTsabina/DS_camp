#!../delmerfi/bin/python3

import timeit
import random
from collections import Counter


def my_func(numbers):
    d = dict()
    for num in numbers:
        d[num] = numbers.count(num)
    return d


def counter_func(numbers):
    counts = Counter(numbers)
    return dict(counts)


def my_top(numbers):
    counts = my_func(numbers)
    top_10 = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return dict(top_10)


def counter_top(numbers):
    ten = Counter(numbers).most_common(10)
    return dict(ten)


if __name__ == '__main__':
    numbers = [random.randint(0, 100) for _ in range(1000000)]
    try:
        my_func_time = timeit.timeit(
            'my_func(numbers)', globals=globals(), number=1)
        counter_time = timeit.timeit(
            'counter_func(numbers)', globals=globals(), number=1)
        my_top_time = timeit.timeit(
            'my_top(numbers)', globals=globals(), number=1)
        cunter_top_time = timeit.timeit(
            'counter_top(numbers)', globals=globals(), number=1)
        print(
            f"my function: {my_func_time:.7f}\nCounter: {counter_time:.7f}\nmy top: {my_top_time:.7f}\nCounter's top: {cunter_top_time:.7f}")
    except Exception as e:
        print(f"Something went wrong: {e}")
