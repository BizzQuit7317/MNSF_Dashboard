import requests
import hmac
import hashlib
import base64
import time
import urllib.parse
import pandas as pd
import datetime

def spot(key, sec):

    api_url = "https://api.kraken.com"
    api_key = key
    api_sec = sec

    def get_kraken_signature(urlpath, data, secret):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def kraken_request(uri_path, data, api_key, api_sec):
        headers = {}
        headers['API-Key'] = api_key
        # get_kraken_signature() as defined in the 'Authentication' section
        headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
        req = requests.post((api_url + uri_path), headers=headers, data=data)
        return req

    resp = kraken_request('/0/private/Balance', {
        "nonce": str(int(1000 * time.time()))
    }, api_key, api_sec)

    return resp.json()

def ledgerID(key, sec):
    api_url = "https://api.kraken.com"
    api_key = key
    api_sec = sec

    def get_kraken_signature(urlpath, data, secret):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def kraken_request(uri_path, data, api_key, api_sec):
        headers = {}
        headers['API-Key'] = api_key
        # get_kraken_signature() as defined in the 'Authentication' section
        headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
        req = requests.post((api_url + uri_path), headers=headers, data=data)
        return req

    resp = kraken_request('/0/private/Ledgers', {
        "nonce": str(int(1000 * time.time()))
    }, api_key, api_sec)

    r = resp.json()
    df = pd.DataFrame(r['result']['ledger'])
    coins = []
    for i in df.iteritems():
        coins.append({"TIME":i[1]['time'], "VENUE":"KRAKEN", "SYMBOL":i[1]['asset'], "TYPE":"REWARD", "SIZE":i[1]['amount'], "Exchange":"Kraken", 'type':i[1]['type'], 'subType':i[1]['subtype']})

    df = pd.DataFrame(coins)
    df = df[(df['type'] == 'staking') & (df['subType'] == '')]
    df['TIME'] = df['TIME'].astype(float) * 1000
    df = df[["TIME", "VENUE", "SYMBOL", "TYPE", "SIZE", "Exchange"]]
    df = df.to_dict(orient='records')
    return df


def get_kraken_current_price(coin):
    resp = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT")
    r = resp.json()
    r = r['price']
    return r

def drops(row):
    if len(row['Coin'].split('.')) == 2:
        return 'EARN'
    else:
        return 'SPOT'

def dropsOG(row):
    if row['Coin'].split('.')[0] == 'DOT28':
        try:
            return 'DOT'
        except:
            return row['Coin'].split('.')[0]
    elif row['Coin'].split('.')[0] =='ETH2':
        try:
            return 'ETH'
        except:
            row['Coin'].split('.')[0]
    elif row['Coin'].split('.')[0] =='GRT28':
        try:
            return 'GRT'
        except:
            row['Coin'].split('.')[0]
    try:
        clean = row['Coin'].split('.')[0]
        return clean
    except:
        return row['Coin']


def calc(row):
    if row['Coin'] == 'DOT28':
        try:
            price = get_kraken_current_price('DOT')
            price = float(price) * float(row['QTY'])
            return price
        except:
            return 0
    elif row['Coin'] == "USDT" or row['Coin'] == "ZUSD" or row['Coin'] == "USD":
        return float(row['QTY'])
    try:
        price = get_kraken_current_price(row['Coin'])
        price = float(price) * float(row['QTY'])
        return price
    except:
        return 0

def kraken_spot_wallet_balance(api_key, api_secret, exchange):
    try:
        spot_wallet = spot(api_key, api_secret)
        data = spot_wallet['result']
        df = pd.DataFrame(list(data.items()), columns=['Coin', 'QTY'])
        df = df[df['QTY'].astype(float) != 0]
        df['Contract'] = df['Coin']
        df['Account'] = df.apply(drops, axis=1)
        df['Coin'] = df.apply(dropsOG, axis=1)
        df['USDValue'] = df.apply(calc, axis=1)
        df['Exchange'] = 'Kraken'
        df['QTY'] =df['QTY'].astype(float)
        df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]
        return df
    except Exception as e:
        print('ERROR WITH SPOT WALLET KRAKEN:     '+str(e))

