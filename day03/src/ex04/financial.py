#!./delmerfi/bin/python3

from bs4 import BeautifulSoup
import requests
import sys
import time

# python -m cProfile -s time financial.py 'apld' 'Total Revenue' > filename.txt


def reciever(ticker):
    url = f'https://finance.yahoo.com/quote/{ticker.upper()}/financials/?p={ticker.lower()}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    return requests.get(url, headers=headers)


def find_field(response, field):
    bs = BeautifulSoup(response.text, 'html.parser')
    quote = bs.find('div', class_='rowTitle yf-t22klz', title=field)
    parent = quote.find_parent()
    siblings = parent.find_next_siblings()
    values = [field]
    for sibling in siblings:
        values.append(sibling.text)
    values = tuple(values)
    return values


def print_data(values):
    if len(values) > 1:
        print(values)
    else:
        print("Couldn't find anydata for your request")


def main(ticker, field):
    try:
        response = reciever(ticker)
        values = find_field(response, field)
        print_data(values)
    except Exception as e:
        print(f"Oooops! Something went wrong: {e}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Too few arguments")
    else:
        main(sys.argv[1], sys.argv[2])
