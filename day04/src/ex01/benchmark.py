#!../delmerfi/bin/python3

import timeit


def common_loop(emails):
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


if __name__ == '__main__':
    emails = ['john@gmail.com', 'james@gmail.com',
              'alice@yahoo.com', 'anna@live.com', 'philipp@gmail.com'] * 5
    loop_time = timeit.timeit('common_loop(emails)',
                              globals=globals(), number=90000000)
    com_time = timeit.timeit('list_comprehension(emails)',
                             globals=globals(), number=90000000)
    map_time = timeit.timeit('map_example(emails)',
                             globals=globals(), number=90000000)
    results = [loop_time, com_time, map_time]
    results.sort()
    if results[0] == loop_time:
        print("it is better to use a loop")
    elif results[0] == map_time:
        print("it is better to use a map")
    else:
        print("it is better to use a list comprehension")
    print(f"{results[0]:.7f} vs {results[1]:.7f} vs {results[2]:.7f}")
