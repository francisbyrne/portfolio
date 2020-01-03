# ['BHP', 'MQG', 'VOC', 'AMM', 'MTS', 'CTD', 'IRI', 'CDA', 'CLH',
#        'RCG', 'COH', 'SIV', 'NHF', 'SOL', 'IMF', 'CBA', 'NAB', 'ABC',
#        'DMG', 'PMV', 'CCV', 'RMD', 'TLS', 'WEB', 'MTU', 'GBT', 'SYD',
#        'TFC', 'CGF', 'FXL', 'GRB', 'CCL', 'TRS', 'PBG', 'CAR', 'MNF',
#        'CPU', 'OFX', 'VRT', 'VTS', 'VAS', 'RFG']
# http://ichart.finance.yahoo.com/table.csv?d=6&e=1&f=2009&g=d&a=7&b=19&c=2004&ignore=.csv&s=

import requests
import file
import os


def make_url(ticker_symbol):
    API_KEY = os.environ['XIGNITE_API_KEY']
    base_url = f"https://www.xignite.com/xGlobalHistorical.csv/GetGlobalHistoricalQuotesRange?_token={API_KEY}&StartDate=7/16/2016&EndDate=7/14/2017&IdentifierType=Symbol&AdjustmentMethod=SplitAndProportionalCashDividend&Identifier="
    return base_url + ticker_symbol


def pull_historical_data(ticker_symbol):
    """Takes a Yahoo Finance ticker symbol and returns the historical data for
        it as a compressed requests session"""
    with requests.Session() as s:
        url = make_url(ticker_symbol)
        return s.get(url)


def write_to_file(content, ticker_symbol):
    path = file.make_path(ticker_symbol)
    with open(path, 'wb') as handle:
        for block in content.iter_content(1024):
            handle.write(block)


def download_hist_data_csv(ticker_symbol, exchange=''):
    if exchange is 'ASX':
        ticker_symbol += '.XASX'
    response = pull_historical_data(ticker_symbol)
    write_to_file(response, ticker_symbol)


def download_all_hist_data(ticker_symbols, exchange='ASX'):
    for symbol in ticker_symbols:
        download_hist_data_csv(symbol, exchange)


download_all_hist_data([
    'BHP', 'MQG', 'VOC', 'AMM', 'MTS', 'CTD', 'IRI', 'CDA', 'CLH',
    'RCG', 'COH', 'SIV', 'NHF', 'SOL', 'IMF', 'CBA', 'NAB', 'ABC',
    'DMG', 'PMV', 'CCV', 'RMD', 'TLS', 'WEB', 'MTU', 'GBT', 'SYD',
    'TFC', 'CGF', 'FXL', 'GRB', 'CCL', 'TRS', 'PBG', 'CAR', 'MNF',
    'CPU', 'OFX', 'VRT', 'VTS', 'VAS', 'RFG'])

# download_all_hist_data(['BHP'])
