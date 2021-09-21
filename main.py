### Program to calculate the the difference between last close price and target prices ###
from datetime import date
import pandas as pd

from config.funcs import get_info


def main():
    today = str(date.today())
    today = today.replace('-', '.')

    # Get list of tickers from downloaded file
    symbols = pd.read_csv('data/symbols.csv', usecols=['Symbol', 'Last Sale', 'Market Cap'])
    symbols['Last Sale'] = symbols['Last Sale'].str.replace('$', '', regex=True).astype(float)
    symbols = symbols[(symbols['Last Sale'] >= 10) & (symbols['Last Sale'] <= 5000)]
    symbols.sort_values('Market Cap', axis=False, ascending=False, inplace=True, na_position='last')
    tickers = symbols['Symbol'].tolist()

    # Ask if user wants to run analysis for tickers
    inp = input(f"Run analysis for {len(tickers)} tickers (y/n)?: ")
    if inp.lower() != "y":
        print("Analysis cancelled.")
    else:
        print("Getting stock info...")
        final_df = get_info(tickers)
        if len(final_df.index) > 0:
            final_df.sort_values('AvgDifference%', axis=False, ascending=False, inplace=True, na_position='last')
            cols = ['LowDifference%', 'AvgDifference%', 'HighDifference%']
            final_df[cols] = final_df[cols].astype(str) + "%"
            final_df.to_csv(f'data/output_{today}.csv', index=False)
            print(f"Analysis complete for {len(final_df.index)} stocks")


if __name__ == '__main__':
    main()
