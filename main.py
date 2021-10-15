### Program to calculate the the difference between last close price and target prices ###
from config.funcs import get_info

from datetime import date
import pandas as pd


def main():
    # Dev toggle
    dev = True

    now = date.today()
    today, df_date = now.strftime('%Y.%m.%d'), now.strftime('%Y/%m/%d')

    # Get list of tickers from downloaded file
    symbols = pd.read_csv('data/symbols.csv', usecols=['Symbol', 'Last Sale', 'Market Cap'])
    symbols['Last Sale'] = symbols['Last Sale'].str.replace('$', '', regex=True).astype(float)
    symbols = symbols[(symbols['Last Sale'] >= 10) & (symbols['Last Sale'] <= 5000)]
    symbols.sort_values('Market Cap', axis=False, ascending=False, inplace=True, na_position='last')
    # Making list of tickers
    if dev:
        tickers = ('DYN', 'FAST', 'AAPL')
    else:
        tickers = set(symbols['Symbol'])

    # Running program to get stock and analyst info
    print(f'Running for {len(tickers)} stocks...')
    final_df = get_info(tickers, dev)
    if len(final_df.index) > 0:
        final_df.sort_values('AvgDifference%', axis=False, ascending=False, inplace=True, na_position='last')
        final_df = final_df[final_df['AvgDifference%'] > 0]  # Remove stocks with a negative average target price
        cols = ['LowDifference%', 'AvgDifference%', 'HighDifference%']
        final_df[cols] = final_df[cols].astype(str) + '%'
        final_df['Rundate'] = df_date

        # Saving the dataframe
        if dev:
            final_df.to_csv(f'data/dev_output_{today}.csv', index=False)
        else:
            final_df.to_csv(f'data/output_{today}.csv', index=False)
        print(f'Analysis complete for {len(final_df.index)} stocks')


if __name__ == '__main__':
    main()
