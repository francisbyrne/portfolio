import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import yfinance as yf
import file


def read_trades_csv():
    """Read in the trades csv and store it in a dataframe"""
    path = file.make_path('trades', '')

    # Read data in from csv file
    # Google Finance has some weird special character in the column name for 'Symbol'
    col_names = ['Date', 'Symbol', 'Type',
                 'Currency', 'Shares', 'Price', 'Commission']
    df = pd.read_csv(path,
                     parse_dates=['Date'],
                     names=col_names,
                     header=0)

    # Drop rows where any column is empty
    df = df.dropna(axis=0)

    return df


def construct_prices_dataframe(symbols, start_date, end_date, benchmark_symbol='^AXJO'):
    """Construct a dataframe of historical prices for the given symbols over
    the given dates"""

    if benchmark_symbol not in symbols:
        symbols.insert(0, benchmark_symbol)

    prices = yf.download(' '.join(symbols), start=start_date,
                         end=end_date, interval="1mo")["Adj Close"]

    # Drop any dates benchmark didn't trade on
    # prices = prices.dropna(subset=[benchmark_symbol])

    prices = prices.fillna(value=0)

    return prices


def normalize_data(df):
    return df / df.ix[0, :]


def plot_data(df, ylabel="Value", title="Portfolio value"):
    ax = df.plot(title=title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    plt.show()

# def plot_individual_stock_prices(symbols, dates):
#     df = construct_prices_dataframe(symbols, dates)
#     df = normalize_data(df)
#     plot_data(df, title="Stock Prices", ylabel="Price")


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

        adjusted_bm_shares = trade.Shares * trade.Price / \
            prices.ix[trade['Date'], benchmark_symbol]
        bm_holding.ix[trade['Date']:] = sign * \
            adjusted_bm_shares * prices[benchmark_symbol]

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
    start_date = trades['Date'].min().strftime(
        "%Y-%m-%d")  # Date of earliest trade
    end_date = datetime.date.today().strftime("%Y-%m-%d")  # Today's date

    # Get historical prices for all traded stocks
    prices = construct_prices_dataframe(symbols, start_date, end_date)

    print(prices.loc("2019-12-31"))

    # US funds skew the pf value due to different non-trading days from the benchmark
    # del prices['VTS.XASX']
    # del prices['VAS.XASX']

    # portfolio = get_portfolio_value_over_time(trades, prices, 'ASX')

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
