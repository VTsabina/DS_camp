#!/bin/python3
import os


if __name__ == '__main__':
    env_path = os.environ.get('VIRTUAL_ENV')
    print(f'Your current virtual env is {env_path}')

# Working in virtual env:
# pip install virtualenv
# virtualenv delmerfi - to create virtual env
# source delmerfi/bin/activate - to activate virtual env
# python3 - opening python console
# in python console:
# >>> import os
# >>> env_path = os.environ.get('VIRTUAL_ENV')
# >>> print(f'Your current virtual env is {env_path}')
# >>> exit() - exiting python console
# ./venv.py - starting the script
# deactivate - to deactivate virtual env
