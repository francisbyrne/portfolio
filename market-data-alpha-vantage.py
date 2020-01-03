from alpha_vantage.timeseries import TimeSeries
import csv
import os
import file


def fetch_csv(ticker):
    ts = TimeSeries(
        key=os.environ['ALPHA_VANTAGE_API_KEY'], output_format='csv')
    data_csv, _ = ts.get_daily(ticker, outputsize='compact')
    return data_csv


def write_to_file(content, ticker):
    path = file.make_path(ticker)
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in content:
            writer.writerow(row)


ticker = 'MQG.AX'
csv_data = fetch_csv(ticker)
write_to_file(csv_data, ticker)
