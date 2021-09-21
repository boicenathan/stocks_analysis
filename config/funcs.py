### Functions ###
from time import time, sleep
from yaml import safe_load
import pandas as pd
import numpy as np
import requests
import json


def wait_time(start):
    end = time()
    total = end - start
    if total < .2:
        wait = .2 - total
        return wait
    else:
        return 0


def get_info(tickers):
    final_df = pd.DataFrame(columns=['Ticker', 'Name', 'PreviousClose', 'LowTargetPrice', 'AvgTargetPrice',
                                     'HighTargetPrice', 'LowDifference%', 'AvgDifference%', 'HighDifference%',
                                     'LowDifference', 'AvgDifference', 'HighDifference', 'Recommendation'])
    with open('config/parameters.yaml') as f:
        creds = safe_load(f)
        headers = {'x-rapidapi-key': creds['key'], 'x-rapidapi-host': creds['host']}
        for tick in tickers:
            url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-analysis?symbol={tick}&region=US"
            start = time()
            response = requests.get(url, headers=headers, timeout=10)
            # Checking if the status code is success
            if int(response.status_code) == 200:
                try:
                    # Collecting info
                    stock = {}
                    data = json.loads(response.text)
                    stock['name'] = data['price'].get('longName')
                    stock['prev_close'] = data['summaryDetail']['previousClose'].get('raw', np.nan)
                    stock['low_target'] = data['financialData']['targetLowPrice'].get('raw', np.nan)
                    stock['avg_target'] = data['financialData']['targetMeanPrice'].get('raw', np.nan)
                    stock['high_target'] = data['financialData']['targetHighPrice'].get('raw', np.nan)
                    stock['recommendation'] = data['financialData'].get('recommendationKey', np.nan)
                    # Calculating and formatting
                    recommendation = stock['recommendation'].replace('_', ' ')
                    low_diff = round(stock['low_target'] - stock['prev_close'], 2)
                    low_diffp = round((low_diff / stock['prev_close']) * 100, 1)
                    avg_diff = round(stock['avg_target'] - stock['prev_close'], 2)
                    avg_diffp = round((avg_diff / stock['prev_close']) * 100, 1)
                    high_diff = round(stock['high_target'] - stock['prev_close'], 2)
                    high_diffp = round((high_diff / stock['prev_close']) * 100, 1)
                    # Adding to dataframe
                    final_df.loc[len(final_df.index)] = [tick, stock['name'], stock['prev_close'], stock['low_target'],
                                                         stock['avg_target'], stock['high_target'], low_diffp,
                                                         avg_diffp, high_diffp, low_diff, avg_diff, high_diffp,
                                                         recommendation]
                except KeyError as error:
                    print(f"KeyError: {error} for {tick}")
                    continue
                # Waiting if faster than .2 seconds
                sleep(wait_time(start))
            # Stops before limit is reached if testing for further development is needed
            elif (int(response.headers['x-ratelimit-requests-remaining']) <= 50) and \
                    (int(response.headers['x-ratelimit-requests-remaining']) > 0):
                print(f"Stopping at 50 or less requests remaining.")
                break
            # If request limit is reached
            elif int(response.status_code) == 429:
                reset_sec = int(response.headers['X-RateLimit-requests-Reset'])
                reset = round(((reset_sec / 60) / 60) / 24, 1)
                print(f"Request limit reached, try again in {reset} days.")
                break
            else:
                print(f"Status code: {response.status_code}")
                break
    return final_df
