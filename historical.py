### Analyze Historical Calculations ###
from config.funcs import historic_info

import glob
import pandas as pd


def historic():
    # Merge all historic files
    paths = glob.glob('data/output_*.csv')
    data = [pd.read_csv(p, sep=',') for p in paths]
    merged_df = pd.concat(data, ignore_index=True)

    # Separate most recent analysis
    merged_df['Rundate'] = pd.to_datetime(merged_df['Rundate'])
    merged_df.sort_values(by=['Rundate'], inplace=True, ascending=False)
    recent_df = merged_df[merged_df['Rundate'] == merged_df['Rundate'].max()]

    # Make list of tickers
    tickers = set(merged_df['Ticker'].tolist())

    # Start historical comparison
    analysis = historic_info(tickers, merged_df)

    # Save dataframe
    analysis.to_csv('data/Tracker.csv', index=False)
    print('done')


if __name__ == '__main__':
    historic()