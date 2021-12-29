### Program to calculate the the difference between last close price and target prices ###
from datetime import date
from time import perf_counter

from requests import Session
import pandas as pd

from config.funcs import get_info, ex_time, requests_remaining


def main():
    # Get list of tickers from downloaded file
    symbols = pd.read_csv('data/symbols.csv', 
                          usecols=['Symbol', 'Last Sale', 'Market Cap'], 
                          dtype={'Symbol': str, 'Last Sale': str, 'Market Cap': float})
    symbols['Last Sale'] = symbols['Last Sale'].str.replace('$', '', regex=True).astype(float)
    symbols = symbols[(symbols['Last Sale'] >= 10) & (symbols['Last Sale'] <= 5000)]
    symbols.sort_values('Market Cap', axis=False, ascending=False, inplace=True, na_position='last')
    symbols.reset_index(drop=True, inplace=True)
    tickers = list(set(symbols['Symbol']))
    
    # Check if we have any requests remaining
    with Session() as session:
        ans = requests_remaining(tickers[0], session)
        tickers = tickers[:ans[2] - 51]
        if ans[2] > 50:
            final_df = get_info(tickers, session)  # Transform the data
            final_df.sort_values('LowDifference%', axis=False, ascending=False, inplace=True, na_position='last')
            final_df = final_df[final_df['Risk'] > 0]  # Remove stocks with a negative risk factor
            cols = ['LowDifference%', 'AvgDifference%', 'HighDifference%']
            final_df[cols] = final_df[cols].astype(str) + '%'

            # Add date and save the results
            now = date.today()
            today, df_date = now.strftime('%Y.%m.%d'), now.strftime('%Y/%m/%d')
            final_df['Rundate'] = df_date
            final_df.to_csv(f'data/output_{today}.csv', index=False)
        else:
            print(ans[1])


if __name__ == '__main__':
    start = perf_counter()
    main()
    ex_time(start)
