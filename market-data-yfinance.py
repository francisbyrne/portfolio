import yfinance as yf
import pandas as pd
import os
import datetime
import csv
import file

BASE_CURRENCY = "USD"


def download_historic_prices(trades):
    # Get symbols of all stocks traded
    symbols = trades.Symbol.unique().tolist()

    for symbol in symbols:
        symbol_trades = trades.loc[trades['Symbol'] == symbol]

        start_date = symbol_trades['Date'].min().strftime("%Y-%m-%d")
        # TODO: Fetch last traded date, if all sold, otherwise today's date
        today = datetime.date.today().strftime("%Y-%m-%d")

        # Download the historic prices from Yahoo Finance
        # TODO: Handle dates when stock isn't traded on the first of the month
        prices = yf.Ticker(symbol).history(
            start=start_date, end=today, interval="1mo")[['Close']]

        # Drop all corporate actions (for simplicity). Later we can separate these out into
        # their own files and use them to calculate portfolio performance
        prices = prices.dropna()

        # If historic prices exist, write them to a CSV file
        if not prices.empty:
            output_file = file.make_path(symbol)
            prices.to_csv(output_file)


def download_forex(trades):
    # Get the currencies of all stocks traded
    currencies = trades.Currency.unique().tolist()

    for currency in currencies:
        # No need to fetch the base currency (no conversion needed)
        if currency == BASE_CURRENCY:
            continue

        currency_trades = trades.loc[trades['Currency'] == currency]

        start_date = currency_trades['Date'].min().strftime("%Y-%m-%d")
        # TODO: Fetch last traded date if all sold, otherwise today's date
        today = datetime.date.today().strftime("%Y-%m-%d")

        # Download the Forex prices with the base currency from Yahoo Finance
        # TODO: Handle dates when forex isn't traded on the first of the month
        forex = yf.Ticker(currency+BASE_CURRENCY+'=X').history(
            start=start_date, end=today, interval="1mo")[['Close']]

        # If historic prices exist, write them to a CSV file
        output_file = file.make_path(currency + BASE_CURRENCY, 'forex')
        forex.to_csv(output_file)


def main():
    trades = file.read_trades_csv()

    download_forex(trades)

    download_historic_prices(trades)


if __name__ == "__main__":
    main()
