#!../delmerfi/bin/python3

import timeit
import sys


def loop(emails):
    gmails = []
    for email in emails:
        if email.split('@')[1] == 'gmail.com':
            gmails.append(email)
    return gmails


def list_comprehension(emails):
    gmails = [email for email in emails if email.split('@')[1] == 'gmail.com']
    return gmails


def map_helper(email):
    if email.split('@')[1] == 'gmail.com':
        return email


def map_example(emails):
    return map(map_helper, emails)


def filter_example(emails):
    gmails = filter(lambda email: email.split('@')[1] == 'gmail.com', emails)
    return gmails


if __name__ == '__main__':
    emails = ['john@gmail.com', 'james@gmail.com',
              'alice@yahoo.com', 'anna@live.com', 'philipp@gmail.com'] * 5
    if len(sys.argv) == 3:
        try:
            if sys.argv[1] == 'map' or sys.argv[1] == 'filter':
                sys.argv[1] += '_example'
            time = timeit.timeit(f'{sys.argv[1]}(emails)',
                                 globals=globals(), number=int(sys.argv[2]))
            print(f'{time:.7f}')
        except:
            print("Wrong argument: incorrect command or number of calls")
