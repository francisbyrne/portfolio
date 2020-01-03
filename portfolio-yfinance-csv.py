import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import file


def get_date_range(trades):
    start_date = trades['Date'].min().strftime(
        "%Y-%m-%d")  # Date of earliest trade
    end_date = datetime.date.today().strftime("%Y-%m-%d")  # Today's date
    return pd.date_range(start_date, end_date, freq="MS")


def read_trades_csv():
    """Read in the trades csv and store it in a dataframe"""
    path = file.make_path('trades', '')

    # Read data in from csv file
    col_names = ['Date', 'Symbol', 'Type',
                 'Currency', 'Shares', 'Price', 'Commission']
    df = pd.read_csv(path,
                     parse_dates=['Date'],
                     names=col_names,
                     header=0)

    # Drop rows where any column is empty
    df = df.dropna(axis=0)

    return df


def read_historical_csv(symbol):
    path = file.make_path(symbol)

    # Read data in from csv file
    try:
        df = pd.read_csv(path,
                         index_col='Date',
                         parse_dates=True,
                         usecols=['Date', 'Close'],
                         na_values=['nan'])

    # If there are any data errors, just print an error and skip this stock
    except ValueError as err:
        print('Failed to read data for: ' + symbol, err)
        return None
    except FileNotFoundError as err:
        print(f'No pricing data for: {symbol}. Skipping this stock.')
        return None

    # Rename close column to symbol name
    df = df.rename(columns={'Close': symbol})

    return df


def construct_prices_dataframe(symbols, dates):
    """Construct a dataframe of historical prices for the given symbols over
    the given dates"""

    prices = pd.DataFrame(index=dates)

    for symbol in symbols:
        dfStock = read_historical_csv(symbol)

        if dfStock is None:
            continue

        # Round to two dec. places
        # dfStock = dfStock.round(2)

        # Join with main dataframe
        prices = prices.join(dfStock)

    prices = prices.fillna(value=0)

    return prices


def normalize_data(df):
    return df / df.ix[0, :]


def plot_data(df, ylabel="Value", title="Portfolio value"):
    ax = df.plot(title=title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    plt.show()


def get_portfolio_value_over_time(trades, prices):
    """Takes a dataframe of trades and returns a dataframe of value each day
    from the earliest trade date to today"""

    # Create a dataframe with the same dates as the prices df
    # (hence excludes non-trading days)
    holdings = pd.DataFrame(data=np.zeros((prices.index.values.size, 1)),
                            index=prices.index.values,
                            columns=['Portfolio'])

    for index, trade in trades.iterrows():
        symbol = trade.Symbol

        # Skip any stocks with no price data
        if symbol not in prices.columns:
            continue

        trade_holding = pd.Series(data=0, index=prices.index.values)

        # Sell trades should subtract the holding
        if trade.Type == 'Buy':
            sign = 1
        else:
            sign = -1

        # Set the holding value after the trade date to be the number of shares
        # traded multiplied by the price on that date
        # adjusted_shares = trade.Shares * trade.Price / prices.ix[trade['Date'], symbol]
        trade_holding.ix[trade['Date']:] = sign * trade.Shares * prices[symbol]

        holdings['Portfolio'] += trade_holding

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
    # del prices['VTS.XASX']
    # del prices['VAS.XASX']

    portfolio = get_portfolio_value_over_time(trades, prices)

    print(portfolio)

    # Get weekly prices, rather than daily
    # portfolio_weekly = portfolio['2014-01-01':'2016-11-22':5]

    # portfolio = portfolio.ix['2016-07-16':'2017-07-14', :]

    # print(portfolio)
    #
    # prices = prices.ix['2016-10-10':'2016-10-20', :]
    #
    # del prices['^AXJO']
    # plot_data(prices)

    # daily_returns = compute_daily_returns(portfolio)
    # daily_returns = compute_rolling_mean(daily_returns)
    # plot_data(daily_returns)


if __name__ == "__main__":
    test_run()
