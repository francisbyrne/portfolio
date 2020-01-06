import os
import pandas as pd

DATA_DIRECTORY = "data"
PRICES_DIRECTORY = "historical_prices"


def make_path(name, parent_dir=PRICES_DIRECTORY):
    """Return CSV file path given filename."""
    output_dir = os.path.join(DATA_DIRECTORY, parent_dir)

    # Make directory if it doesn't already exist
    try:
        os.makedirs(output_dir)
    except FileExistsError:
        pass

    return os.path.join(output_dir, "{}.csv".format(str(name)))


def read_trades_csv():
    """Read in the trades csv and store it in a dataframe"""
    path = make_path('trades', '')

    # Read data in from csv file
    df = pd.read_csv(path,
                     parse_dates=['Date'])

    # Drop rows where any column is empty
    df = df.dropna(axis=0)

    return df
