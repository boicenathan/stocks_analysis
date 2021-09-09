### Functions ###
from time import time, sleep
from yaml import safe_load
import pandas as pd
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
    final_df = pd.DataFrame(columns=['Ticker', 'Name', 'PreviousClose', 'MedTargetPrice', 'MeanTargetPrice',
                                     'MedDifference%', 'MeanDifference%', 'MedDifference', 'MeanDifference',
                                     'Recommendation'])
    with open('config/parameters.yaml') as f:
        creds = safe_load(f)
        headers = {
            'x-rapidapi-key': creds['key'],
            'x-rapidapi-host': creds['host']
        }
        for tick in tickers:
            url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-analysis?symbol={tick}&region=US"
            start = time()
            response = requests.get(url, headers=headers, timeout=10)
            if int(response.status_code) == 200:
                # Collecting info
                data = json.loads(response.text)
                name = data['price']['longName']
                prev_close = data['summaryDetail']['previousClose']['raw']
                med_target = data['financialData']['targetMedianPrice']['raw']
                mean_target = data['financialData']['targetMeanPrice']['raw']
                recommendation = data['financialData']['recommendationKey']
                # Calculating and formatting
                recommendation = recommendation.replace('_', ' ')
                med_diff = round(med_target - prev_close, 2)
                mean_diff = round(mean_target - prev_close, 2)
                med_diffp = round((med_diff / prev_close) * 100, 1)
                mean_diffp = round((mean_diff / prev_close) * 100, 1)
                # Adding to dataframe
                final_df.loc[len(final_df.index)] = [tick, name, prev_close, med_target, mean_target, med_diffp,
                                                     mean_diffp, med_diff, mean_diff, recommendation]
                # Waiting if faster than .2 seconds
                sleep(wait_time(start))
            elif int(response.status_code) == 429:
                heads = response.headers
                reset_sec = int(heads['X-RateLimit-requests-Reset'])
                reset = round(((reset_sec / 60) / 60) / 24, 1)
                print(f"Request limit reached, try again in {reset} days.")
                break
            else:
                print(f"Status code: {response.status_code}")
    return final_df
