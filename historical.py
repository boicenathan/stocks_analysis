### Analyze Historical Calculations ###
from glob import glob
from time import perf_counter

import pandas as pd

from config.funcs import historic_info, ex_time


def historic():
    # Merge all historic files
    paths = glob('data/output_*.csv')
    data = [pd.read_csv(p, sep=',') for p in paths]
    merged_df = pd.concat(data, ignore_index=True)

    # Separate most recent analysis
    merged_df['Rundate'] = pd.to_datetime(merged_df['Rundate'])
    merged_df.sort_values(by=['Rundate'], inplace=True, ascending=False)

    # Make list of tickers and start historicl analysis
    tickers = merged_df['Ticker'].to_list()
    analysis = historic_info(tickers, merged_df)

    # Save dataframe
    analysis.to_csv('data/Tracker.csv', index=False)


if __name__ == '__main__':
    start = perf_counter()
    historic()
    ex_time(start)
