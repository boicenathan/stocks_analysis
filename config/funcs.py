### Functions ###
import json
import os
import requests
from time import asctime, localtime, perf_counter

import numpy as np
import pandas as pd
from tqdm import tqdm


def ex_time(start: float) -> str:
    """ Function to calculte code execution time. """
    hours, rem = divmod(perf_counter() - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Runtime: [{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}] on {asctime(localtime())}.\n")
        

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
        res[0], res[1], res[2] = 0, f"Request limit reached, try again in {reset} days.", int(response.headers['x-ratelimit-requests-remaining'])
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
        except (AttributeError, ValueError, KeyError):
            continue
        except KeyboardInterrupt:
            break

    # Calculating and formatting
    final_df['LowDifference'] = final_df.get('LowTargetPrice').sub(final_df.get('PreviousClose'), fill_value=0)
    final_df['LowDifference%'] = (final_df.get('LowDifference').div(final_df.get('PreviousClose'), fill_value=0) * 100)
    final_df['AvgDifference'] = final_df.get('AvgTargetPrice').sub(final_df.get('PreviousClose'), fill_value=0)
    final_df['AvgDifference%'] = (final_df.get('AvgDifference').div(final_df.get('PreviousClose'), fill_value=0) * 100)
    final_df['HighDifference'] = final_df.get('HighTargetPrice').sub(final_df.get('PreviousClose'), fill_value=0)
    final_df['HighDifference%'] = (final_df.get('HighDifference').div(final_df.get('PreviousClose'), fill_value=0) * 100)
    final_df['Risk'] = ((final_df[['AvgDifference%', 'HighDifference%']].sum(axis=1) / 2) + final_df['LowDifference%']) / 100
    pd.options.display.float_format = "{:,.2f}".format

    return final_df


def historic_info(merged: pd.DataFrame) -> pd.DataFrame:
    check_df = pd.DataFrame()
    for tick in tqdm(list(set(merged['Tick']))):
        df = merged[merged['Tick'] == tick]
        if len(df.index) > 1:  # Make sure there isn't just one historical value
            for index, row in df.iterrows():
                df2 = df[df.index != index]
                # Low target check
                df3 = df2[df2['Rundate'] > row['Rundate']]
                df3 = df3[row['LowTargetPrice'] <= df3['PreviousClose']]
                if len(df3.index) > 0:
                    low = df3.iloc[0]
                    row['LowHit'] = 'Yes'
                    row['LowHitDate'] = low['Rundate']
                    row['LowTriggerPrice'] = low['PreviousClose']
                else:
                    row['LowHit'] = 'No'
                    row['LowHitDate'] = None
                    row['LowTriggerPrice'] = None
                # Avg target check
                df3 = df2[row['AvgTargetPrice'] <= df2['PreviousClose']]
                if len(df3.index) > 0:
                    avg = df3.iloc[0]
                    row['AvgHit'] = 'Yes'
                    row['AvgHitDate'] = avg['Rundate']
                    row['AvgTriggerPrice'] = avg['PreviousClose']
                else:
                    row['AvgHit'] = 'No'
                    row['AvgHitDate'] = None
                    row['AvgTriggerPrice'] = None
                # High target check
                df3 = df2[row['HighTargetPrice'] <= df2['PreviousClose']]
                if len(df3.index) > 0:
                    high = df3.iloc[0]
                    row['HighHit'] = 'Yes'
                    row['HighHitDate'] = high['Rundate']
                    row['HighTriggerPrice'] = high['PreviousClose']
                else:
                    row['HighHit'] = 'No'
                    row['HighHitDate'] = None
                    row['HighTriggerPrice'] = None
                # Consolidate
                check_df = check_df.append(row)
        else:
            continue

    # Calculations
    dates = ['Rundate', 'LowHitDate', 'AvgHitDate', 'HighHitDate']
    check_df[dates] = check_df[dates].apply(pd.to_datetime, errors='coerce')
    check_df['LowDuration'] = (check_df.get('LowHitDate') - check_df.get('Rundate')).dt.days
    check_df['AvgDuration'] = (check_df.get('AvgHitDate') - check_df.get('Rundate')).dt.days
    check_df['HighDuration'] = (check_df.get('HighHitDate') - check_df.get('Rundate')).dt.days
    check_df['LowChange'] = np.where(check_df['LowHit'] == 'Yes', (check_df.get('LowTriggerPrice').sub(check_df.get('PreviousClose'), fill_value=0)).div(check_df.get('PreviousClose')), None)
    check_df['AvgChange'] = np.where(check_df['AvgHit'] == 'Yes', (check_df.get('AvgTriggerPrice').sub(check_df.get('PreviousClose'), fill_value=0)).div(check_df.get('PreviousClose')), None)
    check_df['HighChange'] = np.where(check_df['HighHit'] == 'Yes', (check_df.get('HighTriggerPrice').sub(check_df.get('PreviousClose'), fill_value=0)).div(check_df.get('PreviousClose')), None)
    
    # Organize
    check_df = check_df[['Tick', 'Name', 'PreviousClose', 'LowTargetPrice', 'AvgTargetPrice', 'HighTargetPrice', 
                         'Rundate', 'LowHit', 'LowHitDate', 'LowTriggerPrice', 'LowDuration', 'LowChange',
                         'AvgHit', 'AvgHitDate', 'AvgTriggerPrice', 'AvgDuration', 'AvgChange',
                         'HighHit', 'HighHitDate', 'HighTriggerPrice', 'HighDuration', 'HighChange']]
    
    check_df = check_df.loc[(check_df['LowHit'] == 'Yes') | (check_df['AvgHit'] == 'Yes') | (check_df['HighHit'] == 'Yes')]
    
    return check_df
