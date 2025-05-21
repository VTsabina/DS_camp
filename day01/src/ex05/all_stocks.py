import sys

def get_info(line):

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
    
    for item in line:
        if item.title() not in COMPANIES.keys() and item.upper() not in COMPANIES.values():
            print(f'{item} is an unknown company or an unknown ticker symbol')
            break
        for key, value in COMPANIES.items():
            if item.title() == key:
                print(f'{key} stock price is {STOCKS[COMPANIES[key]]}')
            elif item.upper() == value:
                print(f'{value} is a ticker symbol for {key}')              


if __name__ == '__main__':
    try:
        if len(sys.argv) == 2:
                line = [item.replace(" ", "") for item in sys.argv[1].split(',')]
                if "" not in line:
                    get_info(line)
    except:
        pass