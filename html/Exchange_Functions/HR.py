import requests
from urllib.parse import urlencode
import pandas as pd
import Binance as b

def getToken(api_key, api_secret):
    URL = 'https://auth.hiddenroad.com/oauth/token'
    params = {'client_id':api_key, 'client_secret':api_secret, 'audience':'https://api.hiddenroad.com/v0/', 'grant_type':'client_credentials'}
    response = requests.post(URL, data=params)
    return response.json()

def getEndpoint(api_key, api_secret, endpoint, params=dict):
    URL = 'https://api.hiddenroad.com'+endpoint
    token = getToken(api_key, api_secret)
    header = {'Authorization':str(token['token_type']+' '+str(token['access_token']))}
    response = requests.get(URL, headers=header, params=params)
    return response.json()

def calculate_usd(row):
    try:
        return float(b.coinPrice(row['Coin'])) * float(row['QTY'])
    except:
        pass

def coinUpper(row):
    return row['Coin'].upper()

def walletBalance(api_key, api_secret):
    walletBalance = getEndpoint(api_key, api_secret, '/v0/accountactivity/balances-snapshots', params={'venue':'HRPMASTER'})
    dfs = []
    for i in walletBalance['results']:
        df = pd.DataFrame(i['positions_or_balances'])
        if len(df) != 0:
           dfs.append(df)
    df = pd.concat(dfs, axis=0)
    df.rename(columns={'quantity': 'QTY'}, inplace=True)
    df.rename(columns={'instrument': 'Coin'}, inplace=True)
    df['Coin'] = df.apply(coinUpper, axis=1)
    df['USDValue'] = df.apply(calculate_usd, axis=1)
    df['Contract'] = df['Coin']
    df['Exchange'] = 'HRP'
    df['Account'] = 'SPOT'
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]
    df = df[df['QTY'].astype(float) >= 1]
    return df
