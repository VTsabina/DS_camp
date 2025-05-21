#!../delmerfi/bin/python3

import sys
import resource


def read_file(path):
    with open(path, "r", encoding='utf-8') as file:
        data = file.read().splitlines()
    return data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Incorrect number of argument")
    else:
        data = read_file(sys.argv[1])
        for item in data:
            pass
        usage = resource.getrusage(resource.RUSAGE_SELF)
        peak_memory_usage = usage.ru_maxrss / (1024 * 1024)
        user_mode_time = usage.ru_utime
        system_mode_time = usage.ru_stime
        print(
            f'Peak Memory Usage = {peak_memory_usage:.3f} GB\nUser Mode Time + System Mode Time = {user_mode_time + system_mode_time:.2f}s')
