import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np

def get_date_range(trades):
    start_date = trades['Date'].min().strftime("%Y-%m-%d") # Date of earliest trade
    end_date = datetime.date.today().strftime("%Y-%m-%d") # Today's date
    return pd.date_range(start_date, end_date)

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
        symbol += '.XASX'

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

        # Drop any dates benchmark didn't trade on
        if symbol == benchmark_symbol:
            prices = prices.dropna(subset=[benchmark_symbol])

    prices = prices.fillna(value=0)

    return prices

def normalize_data(df):
    return df / df.ix[0,:]

def plot_data(df, ylabel="Value", title="Portfolio value"):
    ax = df.plot(title=title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    plt.show()

def plot_individual_stock_prices(symbols, dates):
    df = construct_prices_dataframe(symbols, dates)
    df = normalize_data(df)
    plot_data(df, title="Stock Prices", ylabel="Price")

def get_portfolio_value_over_time(trades, prices, exchange='', benchmark_symbol='^AXJO'):
    """Takes a dataframe of trades and returns a dataframe of value each day
    from the earliest trade date to today"""

    # Create a dataframe with the same dates as the prices df
    # (hence excludes non-trading days)
    holdings = pd.DataFrame(data=np.zeros((prices.index.values.size, 2)),
                            index=prices.index.values,
                            columns=['Portfolio', 'Benchmark'])

    for index, trade in trades.iterrows():
        symbol = trade.Symbol
        if exchange is 'ASX':
            symbol += '.XASX'

        # Skip any stocks with no price data
        if symbol not in prices.columns:
            continue

        trade_holding = pd.Series(data=0, index=prices.index.values)
        bm_holding = pd.Series(data=0, index=prices.index.values)

        # Sell trades should subtract the holding
        if trade.Type == 'Buy':
            sign = 1
        else:
            sign = -1

        # Set the holding value after the trade date to be the number of shares
        # traded multiplied by the price on that date
        # adjusted_shares = trade.Shares * trade.Price / prices.ix[trade['Date'], symbol]
        trade_holding.ix[trade['Date']:] = sign * trade.Shares * prices[symbol]

        adjusted_bm_shares = trade.Shares * trade.Price / prices.ix[trade['Date'], benchmark_symbol]
        bm_holding.ix[trade['Date']:] = sign * adjusted_bm_shares * prices[benchmark_symbol]

        holdings['Portfolio'] += trade_holding
        holdings['Benchmark'] += bm_holding

    return holdings

def compute_daily_returns(df):
    # Match rows and columns of original dataframe
    daily_returns = df.copy()

    # Compute daily returns for row 1 onwards
    daily_returns[1:] = (df[1:] / df[:-1].values) - 1

    # Initial row is uncalculatable, so set it to 0
    daily_returns.ix[0, :] = 0

    return daily_returns

def compute_rolling_mean(df, window=30):
    return df.rolling(window).mean()

def test_run():
    trades = read_trades_csv()

    # Get symbols of all stocks traded
    symbols = trades.Symbol.unique().tolist()

    # Define a date range
    dates = get_date_range(trades)

    # Get historical prices for all traded stocks
    prices = construct_prices_dataframe(symbols, dates)

    # US funds skew the pf value due to different non-trading days from the benchmark
    del prices['VTS.XASX']
    del prices['VAS.XASX']

    portfolio = get_portfolio_value_over_time(trades, prices, 'ASX')

    # Get weekly prices, rather than daily
    # portfolio_weekly = portfolio['2014-01-01':'2016-11-22':5]

    portfolio = portfolio.ix['2016-07-16':'2017-07-14', :]

    # print(portfolio)
    #
    # prices = prices.ix['2016-10-10':'2016-10-20', :]
    #
    # del prices['^AXJO']
    # plot_data(prices)

    daily_returns = compute_daily_returns(portfolio)
    daily_returns = compute_rolling_mean(daily_returns)
    plot_data(daily_returns)


if __name__ == "__main__":
    test_run()
