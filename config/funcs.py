### Functions ###
import json
from math import floor
import os
import requests
from time import asctime, localtime

import numpy as np
import pandas as pd
from tqdm import tqdm


def ex_time(start: float, end: float) -> str:
    """ Function to calculte code execution time. """
    total = end - start
    if total < 60:
        print(f"Complete in {round(total, 3)} seconds on {asctime(localtime())}.\n")
    elif total > 3600:
        hrs = total / 3600
        mins = (hrs - floor(hrs)) * 60
        sec = (mins - floor(mins)) * 60
        print(f"Complete in {floor(hrs)} hours, {floor(mins)} minutes, and {round(sec, 2)} seconds on {asctime(localtime())}.\n")
    else:
        mins = total / 60
        sec = (mins - floor(mins)) * 60
        print(f"Complete in {floor(mins)} minutes and {round(sec, 2)} seconds on {asctime(localtime())}.\n")
        

def requests_remaining(tick: str, session: requests.Session) -> list:
    """ Function to determine if there are any request available to pull info. """
    headers = {'x-rapidapi-key': os.getenv('YAHOO_API_KEY1'), 'x-rapidapi-host': os.getenv('YAHOO_API_HOST')}
    response = session.get(
            f'https://yh-finance.p.rapidapi.com/stock/v2/get-analysis?symbol={tick}&region=US',
            headers=headers,
            timeout=10)
    res = [None] * 3
    reset = round(int(response.headers['X-RateLimit-requests-Reset']) / 86400, 1)
    if int(response.status_code) == 429:
        res[0], res[1], res[2] = 0, f"Request limit reached, try again in {reset} days.", 51
    else:
        res[0], res[1], res[2] = 1, f"Request limit reached, try again in {reset} days.", int(response.headers['x-ratelimit-requests-remaining'])
    
    return res
    

def get_info(tickers: list, session: requests.Session) -> pd.DataFrame:
    """ Function to get and transform the stock info. """
    final_df = pd.DataFrame(columns=['Tick', 'Name', 'PreviousClose', 
                                     'LowTargetPrice', 'AvgTargetPrice', 'HighTargetPrice',
                                     'LowDifference', 'AvgDifference', 'HighDifference',
                                     'LowDifference%', 'AvgDifference%', 'HighDifference%',
                                     'Risk', 'Recommendation', 'NumberOfAnalysts'])
    headers = {'x-rapidapi-key': os.getenv('YAHOO_API_KEY1'), 'x-rapidapi-host': os.getenv('YAHOO_API_HOST')}
    
    # Collecting info
    for tick in tqdm(tickers, desc='Pulling Info'):
        stock = {}
        try:
            response = session.get(f'https://yh-finance.p.rapidapi.com/stock/v2/get-analysis?symbol={tick}&region=US', headers=headers)
            data = json.loads(response.text)
            financialdata = data.get('financialData')
            stock['Tick'] = data['price'].get('symbol')
            stock['Name'] = data['price'].get('longName')
            stock['PreviousClose'] = data['summaryDetail']['previousClose'].get('raw', np.nan)
            stock['LowTargetPrice'] = financialdata['targetLowPrice'].get('raw', np.nan)
            stock['AvgTargetPrice'] = financialdata['targetMeanPrice'].get('raw', np.nan)
            stock['HighTargetPrice'] = financialdata['targetHighPrice'].get('raw', np.nan)
            stock['Recommendation'] = financialdata.get('recommendationKey', np.nan)
            stock['NumberOfAnalysts'] = financialdata['numberOfAnalystOpinions'].get('raw', np.nan)
            final_df = final_df.append(stock, ignore_index=True)  # Adding to dataframe
        except (AttributeError, ValueError) as error:
            print(f"Error with {tick}: {error}")
            continue

    # Calculating and formatting
    final_df['LowDifference'] = final_df.get('LowTargetPrice').sub(final_df.get('PreviousClose'), fill_value=0)
    final_df['LowDifference%'] = (final_df.get('LowDifference').div(final_df.get('PreviousClose'), fill_value=0) * 100)
    final_df['AvgDifference'] = final_df.get('AvgTargetPrice').sub(final_df.get('PreviousClose'), fill_value=0)
    final_df['AvgDifference%'] = (final_df.get('AvgDifference').div(final_df.get('PreviousClose'), fill_value=0) * 100)
    final_df['HighDifference'] = final_df.get('HighTargetPrice').sub(final_df.get('PreviousClose'), fill_value=0)
    final_df['HighDifference%'] = (final_df.get('HighDifference').div(final_df.get('PreviousClose'), fill_value=0) * 100)
    final_df['Risk'] = ((final_df[['AvgDifference%', 'HighDifference%']].sum(axis=1) / 2) + final_df['LowDifference%']) / 100

    return final_df


def historic_info(tickers: list, merged: pd.DataFrame) -> pd.DataFrame:
    checking_df = pd.DataFrame(columns=['Ticker', 'LastClose', 'CloseDate', 'TargetReached', 'TargetReachDate'])
    for tick in tqdm(tickers):
        hit_target = hit_date = run_date = []
        temp_df = merged[merged['Ticker'] == tick]
        closes, targets, dates = (temp_df['PreviousClose'].to_numpy(), temp_df['AvgTargetPrice'].to_numpy(),
                                  temp_df['Rundate'].to_numpy())
        for price in closes:
            for target in targets:
                if price >= target:
                    hit_target.append('Yes')
                    r_index = price.index()
                    run_date.append(dates[r_index])
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
