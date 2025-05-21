#!./delmerfi/bin/python3

import os
import sys
import subprocess
from shutil import make_archive

# before starting it's better to renew the venv
# basic req list is: beautifulsoup4 pytest
# source delmerfi/bin/activate
# ./librarian.py
# deactivate


def check_env():
    env_path = os.environ.get('VIRTUAL_ENV')
    env_name = os.path.basename(env_path)
    if env_name != 'delmerfi':
        raise ValueError('Wrong environment')


if __name__ == '__main__':
    try:
        check_env()
    except ValueError:
        print("Wrong environment. Checkout to 'delmerfi'")
    except TypeError:
        print("You're not in virtual environment at all")
    else:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        reqs = subprocess.check_output(
            [sys.executable, '-m', 'pip', 'freeze']).decode('utf-8')
        print(reqs)
        with open("requirements.txt", 'w', encoding='utf-8') as file:
            file.write(reqs)
        env_path = os.path.join(os.getcwd(), 'delmerfi')
        make_archive(env_path, 'zip', 'delmerfi')
