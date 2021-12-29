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
    merged_df = merged_df[['Tick', 'Name', 'PreviousClose', 'LowTargetPrice', 'AvgTargetPrice', 'HighTargetPrice', 'Rundate']]
    pd.options.display.float_format = "{:,.2f}".format

    # Format and sort by rundate
    merged_df['Rundate'] = pd.to_datetime(merged_df['Rundate']).dt.date
    merged_df.sort_values(by=['Rundate'], inplace=True)

    # Start historicl analysis
    analysis = historic_info(merged_df)

    # Save dataframe
    analysis.to_csv('data/HistoricTracker.csv', index=False)


if __name__ == '__main__':
    start = perf_counter()
    historic()
    ex_time(start)
