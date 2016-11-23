import os
import pandas as pd
import datetime
from yahoo_finance import Share

def filename_to_path(name, base_dir="data"):
    """Return CSV file path given filename."""
    return os.path.join(base_dir, "{}.csv".format(str(name)))

def read_trades_csv():
    """Read in the trades csv and store it in a dataframe"""
    path = filename_to_path('trades')

    # Read data in from csv file
    # Google Finance has some weird special character in the column name for 'Symbol'
    col_names = ['Symbol','Type','Date','Shares','Price','Commission']
    df = pd.read_csv(path,
                     parse_dates=['Date'],
                     names=col_names,
                     header=0,
                     usecols=[0,2,3,4,5,7])

    # Drop rows where any column is empty
    df = df.dropna(axis=0)

    return df

def get_historical_data(symbol, start_date, end_date):
    """Pull the historical data from Yahoo Finance and return dataframe"""
    share = Share(symbol + '.AX') # Stock tickers are for ASX
    historical_data = share.get_historical(start_date, end_date)

    return pd.DataFrame(historical_data)

def read_historical_csv(symbol, exchange=''):
    if exchange is 'ASX':
        symbol += '.AX'

    path = filename_to_path(symbol, base_dir='data/historical-prices')

    # Read data in from csv file
    df = pd.read_csv(path,
                     parse_dates=['Date'],
                     usecols=['Date', 'Adj Close'])

    # Drop rows where any column is empty
    df = df.dropna(axis=0)

    return df

def plot_data(df, title="Stock prices"):
    ax = df.plot(title=title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()

def test_run():
    # Define a date range
    dates = pd.date_range('2015-01-01', '2015-12-31')

    # Choose stock symbols to read
    symbols = ['VOC', 'CTD', 'WEB']

    # Get stock data
    df = get_data(symbols, dates)

    df = normalize_data(df)

    # Print subset of data range
    # print(df.ix['2010-03-01':'2010-03-31', ['SPY', 'IBM', 'GOOG']])
    plot_data(df)


if __name__ == "__main__":
    test_run()


# trades = read_trades_csv()
# symbols = trades.Symbol.unique()
# for symbol in symbols:
#     start_date = trades.ix[trades.Symbol==symbol, 'Date'].min().strftime("%Y-%m-%d") # The earliest trade date
#     end_date = datetime.date.today().strftime("%Y-%m-%d") # Today's date
