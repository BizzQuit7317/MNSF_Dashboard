import pandas as pd
import requests, hmac, hashlib, time
from urllib.parse import quote_plus
from pybit.unified_trading import HTTP
import time

def bybit_signature(segreta_bybit, params):
    #timestamp = int(time.time() * 10 ** 3)
    param_str = ''
    for key in sorted(params.keys()):
        v = params[key]
        if isinstance(params[key], bool):
            if params[key]:
                v = 'true'
            else :
                v = 'false'
        param_str += key + '=' + v + '&'
    param_str = param_str[:-1]
    hash = hmac.new(segreta_bybit.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    signature = hash.hexdigest()
    sign_real = {
        "sign": signature
    }
    param_str = quote_plus(param_str, safe="=&")
    full_param_str = f"{param_str}&sign={sign_real['sign']}"
    return full_param_str

def get_bybit_current_price(symbol):
    BASE_URL = 'https://api.bybit.com'
    enpoint = '/v5/market/tickers'
    params = {'category':'linear', 'symbol':symbol+'USDT'}
    url = BASE_URL + enpoint
    response = requests.get(url, params=params)
    r = response.json()
    try:
        return float(r['result']['list'][0]['lastPrice'])
    except:
        return 1

def signed_request(chiave_bybit, segreta_bybit, endpoint):
    BASE_URL = 'https://api.bybit.com'
    enpoint = endpoint
    timestamp = int(time.time() * 10 ** 3)
    params={'api_key':chiave_bybit,
                'timestamp': str(timestamp),
                'recv_window': '5000',
                'accountType':'UNIFIED'}
    full_param_str = bybit_signature(segreta_bybit, params)
    url = BASE_URL + enpoint + '?' + full_param_str
    response = requests.get(url)
    r = response
    r = r.json()
    return r

def get_v5_balance(api_key, api_secret):
    session = HTTP(
        api_key=api_key,
        api_secret=api_secret
    ) 
    balance = session.get_wallet_balance(
    accountType="UNIFIED"
    )  
    return balance

def get_v5_fund(api_key, api_secret):
    session = HTTP(
        api_key=api_key,
        api_secret=api_secret
    ) 
    balance = session.get_coins_balance(
    accountType="FUND"
    )  
    return balance

def get_v5_positions(api_key, api_secret):
    session = HTTP(
        api_key=api_key,
        api_secret=api_secret
    )
    position = session.get_positions(
        category = "linear",
        settleCoin='USDT'
    )
    return position

def get_v5_fundingFees(api_key, api_secret, endtime):
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    fund = (session.get_transaction_log(
        accountType="UNIFIED",
        category="linear",
        currency="USDT",
        limit=50,
        endTime=endtime,
        type="SETTLEMENT"
    ))
    return fund

def get_v5_balance_coin(api_key, api_secret, symbol):
    session = HTTP(
        api_key=api_key,
        api_secret=api_secret
    )
    balance = session.get_wallet_balance(
    accountType="UNIFIED",
    coin=symbol,
    )
    return balance['result']['list'][0]

def net_lev(api_key, api_secret):
    try:
        BTC = get_v5_balance_coin(api_key, api_secret, "BTC")
        ETH = get_v5_balance_coin(api_key, api_secret, "ETH")

        print(f"BTC -> {BTC['coin'][0]['usdValue']}\nETH -> {ETH['coin'][0]['usdValue']}")

        #BTC_price = get_bybit_current_price("BTC")
        #ETH_price = get_bybit_current_price("ETH")

        BTC_lev = float(BTC['coin'][0]['usdValue']) #* float(BTC_price)
        ETH_lev = float(ETH['coin'][0]['usdValue']) #* float(ETH_price)

        #net_lev = BTC_lev + ETH_lev

        #net_lev = float(BTC['totalWalletBalance']) + float(ETH['totalWalletBalance'])
        net_lev = BTC_lev + ETH_lev

        return net_lev
    except:
        return 1

def standardFraming(data, transpose, asset, qty, exchange, account):
    df = pd.DataFrame(data)
    if transpose:
        df = df.T
    df.reset_index(inplace=True)
    df.rename(columns={asset: 'Coin'}, inplace=True)
    df['Contract'] = df['Coin']
    df['QTY'] = df[qty]
    try:
        df['USDValue'] = df.apply(lambda row: row['QTY'] * float(get_bybit_current_price(row['Contract']+'USDT')), axis=1)
    except:
        try:
            df['USDValue'] = df['usdValue']
        except:
            df['USDValue'] = df['QTY']
    df['Exchange'] = exchange
    df['Account'] = account
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]
    df = df[df['QTY'] != 0]

    return df

def calculate_value(row):
    if row['side'] == 'Sell':
        return float(row['size']) * -1
    else:
        return float(row['size'])

def calculate_liqPrice(row):
    if row['LiqPrice'] == '':
        row['LiqPrice'] = 0
    if row['side'] == 'Sell':
        #print(f"SELL: {(float(row['LiqPrice'])-get_bybit_current_price(row['Coin']))/get_bybit_current_price(row['Coin'])}\n####################################\n")
        x = (float(row['LiqPrice'])-get_bybit_current_price(row['Coin']))/get_bybit_current_price(row['Coin'])
        if x < 0:
            x = 1
        return x
    else:
        #print(f"BUY: {(get_bybit_current_price(row['Coin'])-float(row['LiqPrice']))/get_bybit_current_price(row['Coin'])}\n####################################\n")
        x = (get_bybit_current_price(row['Coin'])-float(row['LiqPrice']))/get_bybit_current_price(row['Coin'])
        if x < 0:
            x = 1
        return x

def bybit_futures_wallet(api_key, api_secret, exchange):
    try:
        futures_wallet = signed_request(api_key, api_secret, '/v5/account/wallet-balance')
        try:
            df = standardFraming(futures_wallet, True, 'index', 'equity', exchange, 'USDT-M')

            return df
        except Exception as e:
            print('ERROR WITH FUTURES WALLET BYBIT:     '+str(e))
    except:
        return pd.DataFrame()

def bybit_spot_wallet(api_key, api_secret, exchange):
    spot_wallet = get_v5_balance(api_key, api_secret)
    try:
        df = standardFraming(spot_wallet['result']['list'][0]['coin'], False, 'coin', 'equity', exchange, 'USDT-M')

        return df
    except Exception as e:
        print('ERROR WITH SPOT WALLET BYBIT:     '+str(e))

def bybit_fund_wallet(api_key, api_secret, exchange):
    wallet = get_v5_fund(api_key, api_secret)
    try:
        df = standardFraming(wallet['result']['balance'], False, 'coin', 'walletBalance', exchange, 'SPOT')

        return df
    except Exception as e:
        print('ERROR WITH FUND WALLET BYBIT:     '+str(e))

def total_bybit_balance(api_key, api_secret, exchange):
    df = pd.concat([bybit_futures_wallet(api_key, api_secret, exchange), bybit_spot_wallet(api_key, api_secret, exchange), bybit_fund_wallet(api_key, api_secret, exchange)], ignore_index=True)
    return df

def maint_value(api_key, api_secret):
    session = HTTP(
                api_key=api_key,
                api_secret=api_secret,
            )

    x = session.get_wallet_balance(
        accountType="UNIFIED",
    )
    try:
        return x['result']['list'][0]['totalMaintenanceMargin']
    except:
        return 0

def get_usdt_pos(api_key, api_secret, exchange):
    usdtPos = get_v5_positions(api_key, api_secret)

    try:
        df = pd.DataFrame(usdtPos['result']['list'])
        df.rename(columns={'symbol': 'Coin'}, inplace=True)
        df['Contract'] = df['Coin']
        df['Coin'] = df['Coin'].str[:-4]
        df['QTY'] = df.apply(calculate_value, axis=1)
        df['USDValue'] = df['QTY'].astype(float) * df['markPrice'].astype(float)
        df['Exchange'] = exchange
        df['Account'] = 'USDT-M'
        df['Leverage'] = df['leverage']
        df['MarkPrice'] = df['markPrice']
        df['LiqPrice'] = df['liqPrice']
        df['LiqRisk'] = df.apply(calculate_liqPrice, axis=1)
        df['MaintMargin'] = df.apply(lambda row: maint_value(api_key, api_secret), axis=1)
        df =df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account', 'Leverage', 'MarkPrice', 'LiqPrice', 'LiqRisk', 'MaintMargin']]
        df = df[df['QTY'] != 0]

        return df
    except Exception as e:
        print(f"Error with bybit position: {e}")
