import sys

def get_info_by_ticker(ticker):

    ticker = ticker.upper()

    COMPANIES = {
    'Apple': 'AAPL',
    'Microsoft': 'MSFT',
    'Netflix': 'NFLX',
    'Tesla': 'TSLA',
    'Nokia': 'NOK'
    }

    STOCKS = {
    'AAPL': 287.73,
    'MSFT': 173.79,
    'NFLX': 416.90,
    'TSLA': 724.88,
    'NOK': 3.37
    }

    for key, value in COMPANIES.items():
        if value == ticker:
            return [key, STOCKS[ticker]]


if __name__ == '__main__':
    try:
        if len(sys.argv) == 2:
            print(*get_info_by_ticker(sys.argv[1]))
    except:
        print("Unknown compamy")