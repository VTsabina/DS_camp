import sys

def get_price(company_name):
    
    company_name = company_name.title()

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
    try:
        return STOCKS[COMPANIES[company_name]]
    except KeyError:
        return "Unknown compamy"


if __name__ == '__main__':
    if len(sys.argv) == 2:
        print(get_price(sys.argv[1]))