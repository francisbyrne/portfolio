# ['BHP', 'MQG', 'VOC', 'AMM', 'MTS', 'CTD', 'IRI', 'CDA', 'CLH',
#        'RCG', 'COH', 'SIV', 'NHF', 'SOL', 'IMF', 'CBA', 'NAB', 'ABC',
#        'DMG', 'PMV', 'CCV', 'RMD', 'TLS', 'WEB', 'MTU', 'GBT', 'SYD',
#        'TFC', 'CGF', 'FXL', 'GRB', 'CCL', 'TRS', 'PBG', 'CAR', 'MNF',
#        'CPU', 'OFX', 'VRT', 'VTS', 'VAS', 'RFG']
# http://ichart.finance.yahoo.com/table.csv?d=6&e=1&f=2009&g=d&a=7&b=19&c=2004&ignore=.csv&s=

import requests

def make_url(ticker_symbol):
    base_url = "http://ichart.finance.yahoo.com/table.csv?s="
    return base_url + ticker_symbol

def pull_historical_data(ticker_symbol):
    """Takes a Yahoo Finance ticker symbol and returns the historical data for
        it as a compressed requests session"""
    with requests.Session() as s:
        url = make_url(ticker_symbol)
        return s.get(url)

def make_filepath(ticker_symbol, directory="data/historical-prices"):
    output_path = "."
    return output_path + "/" + directory + "/" + ticker_symbol + ".csv"

def write_to_file(content, ticker_symbol):
    path = make_filepath(ticker_symbol)
    with open(path, 'wb') as handle:
        for block in content.iter_content(1024):
            handle.write(block)

def download_hist_data_csv(ticker_symbol, exchange=''):
    if exchange is 'ASX':
        ticker_symbol += '.AX'
    response = pull_historical_data(ticker_symbol)
    write_to_file(response, ticker_symbol)

def download_all_hist_data(ticker_symbols, exchange='ASX'):
    for symbol in ticker_symbols:
        download_hist_data_csv(symbol, exchange)

# download_all_hist_data([
#     'BHP', 'MQG', 'VOC', 'AMM', 'MTS', 'CTD', 'IRI', 'CDA', 'CLH',
#     'RCG', 'COH', 'SIV', 'NHF', 'SOL', 'IMF', 'CBA', 'NAB', 'ABC',
#     'DMG', 'PMV', 'CCV', 'RMD', 'TLS', 'WEB', 'MTU', 'GBT', 'SYD',
#     'TFC', 'CGF', 'FXL', 'GRB', 'CCL', 'TRS', 'PBG', 'CAR', 'MNF',
#     'CPU', 'OFX', 'VRT', 'VTS', 'VAS', 'RFG'])
