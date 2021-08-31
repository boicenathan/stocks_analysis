### Program to calculate the the difference between last close price and target prices ###
from datetime import date
from yaml import safe_load
from time import sleep, time
import pandas as pd
import requests
import json

from config.funcs import wait_time


def main():
    today = str(date.today())
    today = today.replace('-', '.')

    # Get list of tickers from downloaded file
    symbols = pd.read_csv('data/symbols.csv', usecols=['Symbol', 'Last Sale', 'Market Cap'])  # https://www.nasdaq.com/market-activity/stocks/screener
    symbols['Last Sale'] = symbols['Last Sale'].str.replace('$', '', regex=True).astype(float)
    symbols = symbols[(symbols['Last Sale'] <= 5000) & (symbols['Last Sale'] >= 10)]
    symbols.sort_values('Market Cap', axis=False, ascending=False, inplace=True, na_position='last')
    tickers = symbols['Symbol'].tolist()
    tickers = tickers[:500]  # Due to API limitations on free plan

    # Ask if user wants to run analysis for tickers
    inp = input(f"Run analysis for {len(tickers)} tickers (y/n)?: ")
    if inp.lower() == "y":
        final_df = pd.DataFrame(columns=['Ticker', 'Name', 'PreviousClose', 'MedTargetPrice', 'MeanTargetPrice',
                                         'MedDifference%', 'MeanDifference%', 'MedDifference', 'MeanDifference'])
        with open('config/parameters.yaml') as f:
            creds = safe_load(f)
            headers = {
                'x-rapidapi-key': creds['key'],
                'x-rapidapi-host': creds['host']
            }
            print("Getting stock info...")
            bnum = 0
            for tick in tickers:
                try:
                    url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-analysis?symbol={tick}" \
                          f"&region=US"
                    start = time()
                    response = requests.get(url, headers=headers, timeout=10)
                    data = json.loads(response.text)
                    name = data['price']['longName']
                    prev_close = data['summaryDetail']['previousClose']['raw']
                    med_target = data['financialData']['targetMedianPrice']['raw']
                    mean_target = data['financialData']['targetMeanPrice']['raw']
                    med_diff = round(med_target - prev_close, 2)
                    mean_diff = round(mean_target - prev_close, 2)
                    med_diffp = round((med_diff / prev_close) * 100, 1)
                    mean_diffp = round((mean_diff / prev_close) * 100, 1)
                    final_df.loc[len(final_df.index)] = [tick, name, prev_close, med_target, mean_target, med_diffp,
                                                         mean_diffp, med_diff, mean_diff]
                    sleep(wait_time(start))
                except requests.exceptions.RequestException as err:
                    print(f"Error: {err}"
                          f"\nLocation {tick} ({tickers.index(tick) + 1})")
                    bnum += 1
                    if bnum == 3:
                        print("Exiting after 3 failed attempts.")
                        break
                    else:
                        continue
        final_df.sort_values('MeanDifference%', axis=False, ascending=False, inplace=True, na_position='last')
        final_df[['MedDifference%', 'MeanDifference%']] = final_df[['MedDifference%', 'MeanDifference%']].astype(str) + "%"
        final_df.to_csv(f'data/output_{today}.csv', index=False)
        print(f"Analysis complete"
              f"\n{final_df.head(5)}")
    else:
        print("Analysis cancelled.")


if __name__ == '__main__':
    main()
