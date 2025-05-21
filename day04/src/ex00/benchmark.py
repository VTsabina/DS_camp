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


if __name__ == '__main__':
    emails = ['john@gmail.com', 'james@gmail.com',
              'alice@yahoo.com', 'anna@live.com', 'philipp@gmail.com'] * 5
    loop_time = timeit.timeit('common_loop(emails)',
                              globals=globals(), number=90000000)
    com_time = timeit.timeit('list_comprehension(emails)',
                             globals=globals(), number=90000000)
    if loop_time < com_time:
        print(f"it is better to use a loop\n{loop_time:.7f} vs {com_time:.7f}")
    else:
        print(
            f"it is better to use a list comprehension\n{com_time:.7f} vs {loop_time:.7f}")
