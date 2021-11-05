### Functions ###
from time import time, sleep, asctime, localtime
from math import floor
import pandas as pd
import numpy as np
import requests
import json
import os


def ex_time(start):
    end = time()
    total = end - start
    hr = total / 3600
    mins = (hr - int(hr)) * 60
    sec = (mins - int(mins)) * 60
    if total < 60:
        print(f"Complete in {round(total, 3)} seconds on {asctime(localtime())}.\n")
    elif total > 3600:
        print(f"Complete in {floor(hr)} hours, {floor(mins)} minutes, and {sec} seconds on {asctime(localtime())}.\n")
    else:
        print(f"Complete in {floor(min)} minutes and {sec} seconds on {asctime(localtime())}.\n")


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
                                     'LowDifference', 'AvgDifference', 'HighDifference', 'Risk', 'Recommendation',
                                     'NumberOfAnalysts'])
    headers = {'x-rapidapi-key': os.getenv('YAHOO_API_KEY'), 'x-rapidapi-host': os.getenv('YAHOO_API_HOST')}
    for count, tick in enumerate(tickers):
        start = time()
        response = requests.get(
            f'https://yh-finance.p.rapidapi.com/stock/v2/get-analysis?symbol={tick}&region=US',
            headers=headers,
            timeout=10)
        # Checking if the status code is success
        if int(response.status_code) == 200:
            try:
                # Collecting info
                stock = {}
                data = json.loads(response.text)
                financialdata = data.get('financialData')
                stock['name'] = data['price'].get('longName')
                stock['prev_close'] = data['summaryDetail']['previousClose'].get('raw', np.nan)
                stock['low_target'] = financialdata['targetLowPrice'].get('raw', np.nan)
                stock['avg_target'] = financialdata['targetMeanPrice'].get('raw', np.nan)
                stock['high_target'] = financialdata['targetHighPrice'].get('raw', np.nan)
                stock['recommendation'] = financialdata.get('recommendationKey', np.nan)
                stock['num_analysts'] = financialdata['numberOfAnalystOpinions'].get('raw', np.nan)
                # Calculating and formatting
                low_target, avg_target, high_target, prev_close = (stock.get('low_target'), stock.get('avg_target'),
                                                                   stock.get('high_target'), stock.get('prev_close'))
                low_diff = round(low_target - prev_close, 2)
                low_diffp = round((low_diff / prev_close) * 100, 1)
                avg_diff = round(avg_target - prev_close, 2)
                avg_diffp = round((avg_diff / prev_close) * 100, 1)
                high_diff = round(high_target - prev_close, 2)
                high_diffp = round((high_diff / prev_close) * 100, 1)
                risk = round((((avg_diffp + high_diffp) / 2) + low_diffp) / 100, 2)
                # Adding to dataframe
                final_df.loc[len(final_df.index)] = [tick, stock['name'], stock['prev_close'], stock['low_target'],
                                                     stock['avg_target'], stock['high_target'], low_diffp,
                                                     avg_diffp, high_diffp, low_diff, avg_diff, high_diff,
                                                     risk, stock['recommendation'], stock['num_analysts']]
            except KeyError as error:
                print(f'KeyError: {error} for {tick}')
                continue
            # Waiting if faster than .2 seconds
            sleep(wait_time(start))
        # If request limit is reached
        elif int(response.status_code) == 429:
            reset = round(int(response.headers['X-RateLimit-requests-Reset']) / 86400, 1)
            print(f'Request limit reached, try again in {reset} days.')
            break
        # Stops before limit is reached if testing for further development is needed
        elif int(response.headers['x-ratelimit-requests-remaining']) <= 50:
            print(f'Stopping at 50 or less requests remaining.')
            break
        # Break if the status code is in the 400's
        elif (int(response.status_code) >= 400) and (int(response.status_code) < 500):
            break
        else:
            print(f'Status code: {response.status_code}')
            continue
    return final_df


def historic_info(tickers, merged):
    checking_df = pd.DataFrame(columns=['Ticker', 'LastClose', 'CloseDate', 'TargetReached', 'TargetReachDate'])
    for tick in tickers:
        hit_target = hit_date = []
        temp_df = merged[merged['Ticker'] == tick]
        closes, targets, dates = (temp_df['PreviousClose'].tolist(), temp_df['AvgTargetPrice'].tolist(),
                                  temp_df['Rundate'].tolist())
        for price in closes:
            for target in targets:
                if price >= target:
                    hit_target.append('Yes')
                    r_index = price.index()
                    run_date = dates[r_index]
                    h_index = target.index()
                    hit_date.append(dates[h_index])
                else:
                    hit_target.append('No')
                    hit_date.append(np.nan)
                    run_date.append(np.nan)
            checking_df.loc[len(checking_df.index)] = [tick, price, run_date, hit_target, hit_date]

        # Calculate time difference and add it to the dataframe
        checking_df['TimeToHit'] = (checking_df.hit_date - checking_df.run_date).days
    return checking_df
