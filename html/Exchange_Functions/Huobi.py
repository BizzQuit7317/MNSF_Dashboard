import pandas as pd
import requests, hmac, hashlib, base64
from urllib.parse import urlencode
from datetime import datetime

def get_huobi_current_price(base, quote):
    symbol = base+quote
    endpoint = '/market/detail/merged'
    base_uri = 'api.huobi.pro'
    method = 'GET'
    url = 'https://' + base_uri + endpoint + '?symbol=' + symbol.lower()
    response = requests.request(method, url)
    r = response.json()
    pr = (r['tick']['bid'][0] + r['tick']['ask'][0])/2
    return pr

def huobi_send_signed_request(chiave_huobi, segreta_huobi, endpoint, method, base_uri):
    timestamp = str(datetime.utcnow().isoformat())[0:19]
    params = urlencode({'AccessKeyId': chiave_huobi,
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Timestamp': timestamp,
                       })
    pre_signed_text = method + '\n' + base_uri + '\n' + endpoint + '\n' + params
    hash_code = hmac.new(segreta_huobi.encode(), pre_signed_text.encode(), hashlib.sha256).digest()
    signature = urlencode({'Signature': base64.b64encode(hash_code).decode()})
    url = 'https://' + base_uri + endpoint + '?' + params + '&' + signature
    response = requests.request(method, url)
    return response.json()

def huobi_send_signed_requestAS(chiave_huobi, segreta_huobi, endpoint, method, base_uri):
    timestamp = str(datetime.utcnow().isoformat())[0:19]
    params = urlencode({'AccessKeyId': chiave_huobi,
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Timestamp': timestamp,
                        'account_type':1
                       })
    pre_signed_text = method + '\n' + base_uri + '\n' + endpoint + '\n' + params
    hash_code = hmac.new(segreta_huobi.encode(), pre_signed_text.encode(), hashlib.sha256).digest()
    signature = urlencode({'Signature': base64.b64encode(hash_code).decode()})
    url = 'https://' + base_uri + endpoint + '?' + params + '&' + signature
    response = requests.request(method, url)
    return response.json()

def huobi_send_signed_request_usdM(chiave_huobi, segreta_huobi, huobi_spot_id, endpoint, method, base_uri):
    timestamp = str(datetime.utcnow().isoformat())[0:19]
    params = urlencode({'AccessKeyId': chiave_huobi,
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Timestamp': timestamp,
                       })
    pre_signed_text = method + '\n' + base_uri + '\n' + endpoint + '\n' + params
    hash_code = hmac.new(segreta_huobi.encode(), pre_signed_text.encode(), hashlib.sha256).digest()
    signature = urlencode({'Signature': base64.b64encode(hash_code).decode()})
    url = 'https://' + base_uri + endpoint + '?' + params + '&' + signature
    response = requests.request(method, url, json={'valuation_asset': 'USDT'})
    return response.json()

def get_contract_size(symbol):
    endpoint = '/swap-api/v1/swap_contract_info?contract_code='+symbol['contract_code']
    base_uri = 'api.hbdm.com'
    method = 'GET'
    url = 'https://' + base_uri + endpoint
    response = requests.request(method, url)
    resp = response.json()
    try:
        return resp['data'][0]['contract_size']
    except:
        return 1

def standardFrame(data, balance, qty, usdFlag, exchange, account):
    df = pd.DataFrame(data)
    df.rename(columns={balance: 'Coin'}, inplace=True)
    df['Contract'] = df['Coin']
    df.rename(columns={qty: 'QTY'}, inplace=True)
    if usdFlag:
        try:
            df['USDValue'] = df.apply(lambda row: row['QTY'] * float(get_huobi_current_price(row['Contract'], 'USDT')), axis=1)
        except:
            df['USDValue'] = df.apply(lambda row: row['QTY'], axis=1)
    else:
        df['USDValue'] = df['QTY']
    df['Exchange'] = exchange
    df['Account'] = account
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]

    return df

def calculate_qty(row):
    if row['direction'] == 'sell':
        return (float(row['contract_size'])*float(row['volume']))*-1
    else:
        return (float(row['contract_size'])*float(row['volume']))

def calculate_liq(row):
    if row['direction'] == 'sell':
        return (float(row['LiqPrice'])-float(row['MarkPrice']))/float(row['MarkPrice'])
    else:
        return (float(row['MarkPrice'])-float(row['LiqPrice']))/float(row['MarkPrice'])

def huobi_usdM_wallet_balance(api_key, api_secret, spot_id, exchange):
    huobi_usdM_wallet = huobi_send_signed_request_usdM(api_key, api_secret, spot_id, '/linear-swap-api/v1/swap_balance_valuation', 'POST', 'api.hbdm.com')
    try:
        df = standardFrame(huobi_usdM_wallet['data'], 'valuation_asset', 'balance', False, exchange, 'USDT-M')

        return df
    except Exception as e:
        print('ERROR WITH USDM WALLET HUOBI:     '+str(e))

def huobi_coinM_wallet_balance(api_key, api_secret, exchange):
    coinM_wallet = huobi_send_signed_request(api_key, api_secret, '/swap-api/v1/swap_account_info', 'POST', 'api.hbdm.com')
    try:
        df = standardFrame(coinM_wallet['data'], 'symbol', 'margin_balance', True, exchange, 'Coin-M')
        df = df[df['QTY'] != 0]

        return df
    except Exception as e:
        print('ERROR WITH COINM WALLET HUOBI:     '+str(e))

def rest_huobi_spot_wallet(chiave_huobi, segreta_huobi, huobi_spot_account_id ,exchange):
    endpoint = '/v1/account/accounts/{}/balance'.format(huobi_spot_account_id)
    r = huobi_send_signed_request(chiave_huobi, segreta_huobi, endpoint, 'GET', 'api.huobi.pro')
    try:
        df = standardFrame(r['data']['list'], 'currency', 'balance', False, exchange, 'SPOT')

        return df
    except Exception as e:
        print('ERROR WITH SPOT WALLET HUOBI:     '+str(e))

def total_huobi_balance(chiave_huobi, segreta_huobi, huobi_spot_account_id, exchange):
    df = pd.concat([rest_huobi_spot_wallet(chiave_huobi, segreta_huobi, huobi_spot_account_id ,exchange), huobi_coinM_wallet_balance(chiave_huobi, segreta_huobi, exchange), huobi_usdM_wallet_balance(chiave_huobi, segreta_huobi, huobi_spot_account_id, exchange)], ignore_index=True)
    return df

def get_usdtM_pos(api_key, api_secret, exchange):
    usdtMPos = huobi_send_signed_request(api_key, api_secret, '/linear-swap-api/v1/swap_cross_position_info', 'POST', 'api.hbdm.com')
    get_cont_size=huobi_send_signed_request(api_key, api_secret, '/linear-swap-api/v1/swap_contract_info', 'GET', 'api.hbdm.com')
    liq_price = huobi_send_signed_request(api_key, api_secret, '/linear-swap-api/v1/swap_cross_account_info', 'POST', 'api.hbdm.com')
    try:
        df = pd.DataFrame(usdtMPos['data'])
        dfx = pd.DataFrame(get_cont_size['data'])
        dfy = pd.DataFrame(liq_price['data'][0]['contract_detail'])
        df = df.merge(dfx, left_on='symbol', right_on='symbol', how='inner', suffixes=('', '_df'))
        df = df.merge(dfy, left_on='symbol', right_on='symbol', how='inner', suffixes=('', '_df'))
        df.rename(columns={'symbol': 'Coin'}, inplace=True)
        df.rename(columns={'contract_code': 'Contract'}, inplace=True)
        df['QTY'] = df.apply(calculate_qty, axis=1)
        df['USDValue'] = df['QTY'].astype(float)*df['last_price'].astype(float)
        df['Exchange'] = exchange
        df['Account'] = 'USDT-M'
        df.rename(columns={'lever_rate': 'Leverage'}, inplace=True)
        df.rename(columns={'last_price': 'MarkPrice'}, inplace=True)
        try:
            df['LiqPrice'] = df['liquidation_price']
            df['LiqRisk'] = df.apply(calculate_liq, axis=1)
        except:
            df['LiqPrice'] = None
            df['LiqRisk'] = None
        df['MaintMargin'] = 0
        df =df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account', 'Leverage', 'MarkPrice', 'LiqPrice', 'LiqRisk', 'MaintMargin']]
        df = df[df['QTY'] != 0]

        return df
    except Exception as e:
        print('ERROR WITH USDTMPOS WALLET HUOBI:     '+str(e))

def get_coinM_pos(api_key, api_secret, exchange):
    coinMPos = huobi_send_signed_request(api_key, api_secret, '/swap-api/v1/swap_position_info', 'POST', 'api.hbdm.com')
    liqPrice = huobi_send_signed_request(api_key, api_secret, '/swap-api/v1/swap_account_info', 'POST', 'api.hbdm.com')
    try:
        df = pd.DataFrame(coinMPos['data'])
        dfx = pd.DataFrame(liqPrice['data'])
        df = df.merge(dfx, left_on='symbol', right_on='symbol', how='inner', suffixes=('', '_df'))
        df['contract_size'] = df.apply(get_contract_size, axis=1)
        df.rename(columns={'symbol': 'Coin'}, inplace=True)
        df.rename(columns={'contract_code': 'Contract'}, inplace=True)
        df['USDValue'] = df.apply(calculate_qty, axis=1)
        df['QTY'] = df['USDValue'].astype(float)/df['last_price'].astype(float)
        df['Exchange'] = exchange
        df['Account'] = 'COIN-M'
        df.rename(columns={'lever_rate': 'Leverage'}, inplace=True)
        df.rename(columns={'last_price': 'MarkPrice'}, inplace=True)
        try:
            df['LiqPrice'] = df['liquidation_price']
            df['LiqRisk'] = df.apply(calculate_liq, axis=1)
        except:
            df['LiqPrice'] = None
            df['LiqRisk'] = None
        df['MaintMargin'] = 0
        df =df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account', 'Leverage', 'MarkPrice', 'LiqPrice', 'LiqRisk', 'MaintMargin']]
        df = df[df['QTY'] != 0]

        return df
    except Exception as e:
        print('ERROR WITH COINMPOS WALLET HUOBI:     '+str(e))

def get_all_positions(api_key, api_secret, exchange):
    try:
        df = pd.concat([get_coinM_pos(api_key, api_secret, exchange), get_usdtM_pos(api_key, api_secret, exchange)], ignore_index=True)
        return df
    except Exception as e:
        print('ERROR WITH ALLPOSITIONS WALLET HUOBI:     '+str(e))
