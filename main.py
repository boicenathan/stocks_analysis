### Program to calculate the the difference between last close price and target prices ###
from config.funcs import get_info, ex_time

from datetime import date
from time import time
import pandas as pd


def main():
    now = date.today()
    today, df_date = now.strftime('%Y.%m.%d'), now.strftime('%Y/%m/%d')

    # Get list of tickers from downloaded file
    symbols = pd.read_csv('data/symbols.csv', usecols=['Symbol', 'Last Sale', 'Market Cap'])
    symbols['Last Sale'] = symbols['Last Sale'].str.replace('$', '', regex=True).astype(float)
    symbols = symbols[(symbols['Last Sale'] >= 10) & (symbols['Last Sale'] <= 5000)]
    symbols.sort_values('Market Cap', axis=False, ascending=False, inplace=True, na_position='last')

    # Making list of tickers and running program to get stock and analyst info
    tickers = set(symbols['Symbol'])
    print(f'Running for {len(tickers)} stocks...')
    final_df = get_info(tickers)
    total = len(final_df.index)
    if total > 0:
        final_df.sort_values('AvgDifference%', axis=False, ascending=False, inplace=True, na_position='last')
        # Remove stocks with a negative risk factor
        final_df = final_df[final_df['Risk'] > 0]
        cols = ['LowDifference%', 'AvgDifference%', 'HighDifference%']
        final_df[cols] = final_df[cols].astype(str) + '%'
        final_df['Rundate'] = df_date

        # Save the results
        final_df.to_csv(f'data/output_{today}.csv', index=False)
        print(f'Analysis complete for {total} stocks.'
              f'\n{total - len(final_df.index)} stock(s) excluded due to negative risk factor.')


if __name__ == '__main__':
    start = time()
    main()
    ex_time(start)
