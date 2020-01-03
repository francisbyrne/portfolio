import os

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
