import yfinance as yf
import pandas as pd
import os
import datetime
import csv
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


def main():
    all_trades = read_trades_csv()

    # Get symbols of all stocks traded
    symbols = all_trades.Symbol.unique().tolist()

    for symbol in symbols:
        symbol_trades = all_trades.loc[all_trades['Symbol'] == symbol]

        start_date = symbol_trades['Date'].min().strftime("%Y-%m-%d")
        today = datetime.date.today().strftime("%Y-%m-%d")

        # Download the historic prices from Yahoo Finance
        # TODO: Handle dates when stock isn't traded on the first of the month
        # TODO: Handle multiple currencies
        prices = yf.Ticker(symbol).history(
            start=start_date, end=today, interval="1mo")[['Close']]

        # Drop all corporate actions (for simplicity). Later we can separate these out into
        # their own files and use them to calculate portfolio performance
        prices = prices.dropna()

        # If historic prices exist, write them to a CSV file
        if not prices.empty:
            output_file = file.make_path(symbol)
            prices.to_csv(output_file)


if __name__ == "__main__":
    main()
