import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime

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

def read_historical_csv(symbol, exchange=''):
    if exchange is 'ASX':
        symbol += '.AX'

    path = filename_to_path(symbol, base_dir='data/historical-prices')

    # Read data in from csv file
    try:
        df = pd.read_csv(path,
                     index_col='Date',
                     parse_dates=True,
                     usecols=['Date', 'Adj Close'],
                     na_values=['nan'])

    # If there are any data errors, just print an error and skip this stock
    except ValueError as err:
        print('Failed to read data for: ' + symbol, err)
        return None

    # Rename adj close column to symbol name
    df = df.rename(columns={'Adj Close': symbol})

    return df

def construct_prices_dataframe(symbols, dates, benchmark_symbol='^AXJO'):
    """Construct a dataframe of historical prices for the given symbols over
    the given dates"""

    prices = pd.DataFrame(index=dates)

    if benchmark_symbol not in symbols:
        symbols.insert(0, benchmark_symbol)

    for symbol in symbols:
        if symbol is benchmark_symbol:
            exchange = ''
        else:
            exchange = 'ASX'

        dfStock = read_historical_csv(symbol, exchange=exchange)

        if dfStock is None:
            continue

        # Round to two dec. places
        # dfStock = dfStock.round(2)

        # Join with main dataframe
        prices = prices.join(dfStock)

        # Drop any dates SPY didn't trade on
        if symbol == benchmark_symbol:
            prices = prices.dropna(subset=[benchmark_symbol])

    return prices

def normalize_data(df):
    return df / df.ix[0,:]

def plot_data(df, title="Stock prices"):
    ax = df.plot(title=title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()

def plot_individual_stock_prices(symbols, dates):
    df = construct_prices_dataframe(symbols, dates)
    df = normalize_data(df)
    plot_data(df)

def test_run():
    trades = read_trades_csv()

    # Define a date range
    start_date = trades['Date'].min().strftime("%Y-%m-%d") # The earliest trade date
    end_date = datetime.date.today().strftime("%Y-%m-%d") # Today's date
    dates = pd.date_range(start_date, end_date)

    # Get symbols of all stocks traded
    symbols = trades.Symbol.unique().tolist()

    # Get historical prices for all traded stocks
    prices = construct_prices_dataframe(symbols, dates)





if __name__ == "__main__":
    test_run()
