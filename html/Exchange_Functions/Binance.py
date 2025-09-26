import requests, time, hmac, hashlib
from urllib.parse import urlencode
import pandas as pd

def calculate_value(row):
    if float(row['positionAmt']) < 0:
        # Execute the formula for negative positionAmt
        #return ((float(row['liquidationPrice']) - float(row['markPrice'])) / float(row['markPrice']))
        risk = ((float(row['liquidationPrice']) - float(row['markPrice'])) / float(row['markPrice']))
    else:
        # Execute the formula for positive positionAmt
        #return ((float(row['markPrice']) - float(row['liquidationPrice'])) / float(row['markPrice']))
        risk = ((float(row['markPrice']) - float(row['liquidationPrice'])) / float(row['markPrice']))
    if risk <= 0:
        risk = 1
    return risk

def coinPrice(coinName):
    try:
        return requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+coinName.upper()+'USDT').json()['price']
    except:
        return 1

def basicFraming(dataList, removalList, balanceName):
    df = pd.DataFrame(dataList)
    df = df[df[balanceName] != '0.00000000']
    df.drop(removalList, axis=1, inplace=True)

    return df

def standardFraming(dataList, exchange, account, conditionIndexList, condition, qtyList, asset):
    df = pd.DataFrame(dataList)
    if len(conditionIndexList) >= 1:
        df = df[df[conditionIndexList[0]] != condition]
    else:
        df = df[(df[conditionIndexList[0]] != condition) & (df[conditionIndexList[1]] != condition)]
    df['Contract'] = df[asset]
    df.rename(columns={asset: 'Coin'}, inplace=True)
    if len(qtyList) <= 1:
        df['QTY'] = df[qtyList[0]].astype(float)
    else:
        df['QTY'] = df[qtyList[0]].astype(float) + df[qtyList[1]].astype(float)
    df['USDValue'] = df.apply(lambda row: row['QTY'] * float(coinPrice(row['Contract'])), axis=1)
    df['Exchange'] = exchange
    df['Account'] = account
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]
    return df

def binance_send_signed_request(BASE_URL, http_method, url_path, chiave_binance, segreta_binance, payload={}):
    query_string = urlencode(payload, True)
    if query_string:
        query_string = "{}&timestamp={}".format(query_string, binance_get_timestamp())  
    else:
        query_string = "timestamp={}".format(binance_get_timestamp())

    url = (
        BASE_URL + url_path + "?" + query_string + "&signature=" + binance_hashing(query_string, segreta_binance)
    )
    params = {"url": url, "params": {}}
    response = binance_dispatch_request(http_method, chiave_binance)(**params)
    return response.json()

def binance_dispatch_request(http_method, chiave_binance=''):
    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": chiave_binance}
    )
    return {
        "GET": session.get,
        "DELETE": session.delete,
        "PUT": session.put,
        "POST": session.post,
    }.get(http_method, "GET")

def get_binance_current_price(base, quote):
    BASE_URL = "https://api.binance.com"
    pr = binance_send_public_request(BASE_URL, '/api/v3/ticker/price', payload={'symbol':base+quote})['price']
    return float(pr)

def binance_get_timestamp():
    return int(time.time() * 1000)

def binance_hashing(query_string, segreta_binance):
    return hmac.new(
        segreta_binance.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

def binance_send_public_request(BASE_URL, url_path, payload={}):
    query_string = urlencode(payload, True)
    url = BASE_URL + url_path
    if query_string:
        url = url + "?" + query_string
    response = binance_dispatch_request("GET")(url=url)
    return response.json()

def binance_future_wallet_balance(api_key, api_secret, exchange):
    futures_wallet = binance_send_signed_request("https://fapi.binance.com", 'GET', '/fapi/v2/balance', api_key, api_secret, payload={})
    try:
        df = standardFraming(futures_wallet, exchange, 'USDT-M', ['balance'], '0.00000000', ['balance', 'crossUnPnl'], 'asset')
        return df
    except Exception as e:
        print('ERROR WITH FUTURE WALLET BINANCE:     '+str(e))

def binance_m_wallet_balance(api_key, api_secret, exchange):
    m_wallet = binance_send_signed_request('https://dapi.binance.com', "GET", '/dapi/v1/balance', api_key, api_secret, payload={})
    try:
        df = standardFraming(m_wallet, exchange, 'COIN-M', ['balance'], '0.00000000', ['balance', 'crossUnPnl'], 'asset')
        return df
    except Exception as e:
        print('ERROR WITH M_ WALLET:     '+str(e))

def net_lev(api_key, api_secret):
    try:
        x = binance_send_signed_request('https://fapi.binance.com', "GET", "/fapi/v2/account", api_key, api_secret,  payload={})
        df = pd.DataFrame(x['assets'])
        df = df[(df['asset'] == 'BTC') | (df['asset'] == 'ETH')]
        df['asset_price'] = df.apply(get_price, axis=1)
        df['walletBalance'] = df['walletBalance'].astype(float) * df['asset_price'].astype(float)
        df['walletBalance'] = df['walletBalance'].astype(float)
        y = df['walletBalance'].sum()
        return y
    except:
        return 0

def get_price(row):
    price = get_binance_current_price(row['asset'], 'USDT')
    return price


def binance_spot_wallet_balance(api_key, api_secret, exchange):
    spot_wallet = binance_send_signed_request('https://api.binance.com', "GET", "/sapi/v1/capital/config/getall", api_key, api_secret, payload={'type': 'SPOT'})
    try:
        df = pd.DataFrame(spot_wallet)
        df = df[(df['locked'] != '0') | (df['free'] != '0')]
        df.rename(columns={'coin': 'Coin'}, inplace=True)
        df['Contract'] = df['Coin']
        df['Exchange'] = exchange
        df['Account'] = 'SPOT'
        df['QTY'] = df['locked'].astype(float) + df['free'].astype(float)
        df['USDValue'] = df.apply(lambda row: row['QTY'] * float(coinPrice(row['Contract'])), axis=1)
        df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]
        return df
    except Exception as e:
        print('ERROR WITH spot WALLET BINANCE:     '+str(e))


def binance_margin_wallet_balance(api_key, api_secret, exchange):
    margin_wallet = binance_send_signed_request('https://api.binance.com', "GET", "/sapi/v1/margin/account", api_key, api_secret, payload={})
    isolated_margin = binance_send_signed_request("https://api.binance.com", 'GET', '/sapi/v1/margin/isolated/account', api_key, api_secret, payload={})
    try:
        df = standardFraming(margin_wallet['userAssets'], exchange, 'MARGIN', ['free'], '0', ['netAsset'], 'asset')
        try:
            dfy = standardFraming(isolated_margin, exchange, 'Margin-Isolated', ['borrowed'], '0', ['netAsset'], 'asset')

            df = pd.concat([df, dfy], ignore_index=True)
        except:
            pass
        return df
    except Exception as e:
        print('ERROR WITH MARGIN WALLET BINANCE:     '+str(e))

def binance_earn_wallet_balance(api_key, api_secret, exchange):
    staking = binance_send_signed_request('https://api.binance.com', "GET", "/sapi/v1/staking/position",api_key, api_secret, payload={'product': 'STAKING'})
    #saving = binance_send_signed_request('https://api.binance.com', "GET", "/sapi/v1/lending/union/account", api_key, api_secret)
    locked = binance_send_signed_request('https://api.binance.com', "GET", "/sapi/v1/simple-earn/flexible/position",api_key, api_secret, payload={})
    worked = []
    try:
        try:
            df = standardFraming(staking, exchange, 'EARN', ['amount'], '0', ['amount'], 'asset')
            worked.append(df)
        except:
            pass
        #try:
        #    dfy = standardFraming(saving['positionAmountVos'], exchange, 'EARN', ['amountInUSDT'], '0', ['amountInUSDT'], 'assets') #Need to swap QTY and USDValue
        #    worked.append(dfy)
        #except:
        #    pass
        try:
            dfz = standardFraming(locked['rows'], exchange, 'EARN', ['collateralAmount', 'cumulativeTotalRewards'], '0.0000', ['collateralAmount', 'cumulativeTotalRewards'], 'asset')
            worked.append(dfz)
        except:
            pass

        df = pd.concat(worked, ignore_index=True)
        return df
    except Exception as e:
        print('ERROR WITH EARN WALLET BINANCE:     '+str(e))

def totalBinance(api_key, api_secret, exchange):
#    try:
#        df = pd.concat([binance_earn_wallet_balance(api_key, api_secret, exchange), binance_margin_wallet_balance(api_key, api_secret, exchange), binance_spot_wallet_balance(api_key, api_secret, exchange), binance_m_wallet_balance(api_key, api_secret, exchange), binance_future_wallet_balance(api_key, api_secret, exchange)], ignore_index=True)
#    except:
#        df = pd.concat([binance_margin_wallet_balance(api_key, api_secret, exchange), binance_spot_wallet_balance(api_key, api_secret, exchange), binance_m_wallet_balance(api_key, api_secret, exchange), binance_future_wallet_balance(api_key, api_secret, exchange)], ignore_index=True)
#    return df
    df = pd.DataFrame()
    for i in ["binance_earn_wallet_balance(api_key, api_secret, exchange)", "binance_margin_wallet_balance(api_key, api_secret, exchange)", "binance_spot_wallet_balance(api_key, api_secret, exchange)", "binance_m_wallet_balance(api_key, api_secret, exchange)", "binance_future_wallet_balance(api_key, api_secret, exchange)"]:
        try:
            df = pd.concat([df, eval(i)], ignore_index=True)
        except:
            pass
    return df

def maint_value(api_key, api_secret):
    r = binance_send_signed_request("https://fapi.binance.com", 'GET', '/fapi/v2/account', api_key, api_secret, payload={})['totalMaintMargin']
    return r

def get_usdt_pos(api_key, api_secret, exchange):
    usdtPos = binance_send_signed_request("https://fapi.binance.com", 'GET', '/fapi/v2/positionRisk', api_key, api_secret, payload={})
    df = pd.DataFrame(usdtPos)
    #df = df[df['positionAmt'].astype(float) != 0]
    df = df[(df['positionAmt'].astype(float) != 0) | (df['unRealizedProfit'].astype(float) != 0)]
    df['Coin'] = df.apply(isolate_coin, axis=1)
    #df['Coin'] = df['symbol'].str[:-4]
    df['Contract'] = df['symbol']
    df['QTY'] = df['positionAmt'].astype(float)  #* 1000
    df['USDValue'] = df['QTY'].astype(float) * df['markPrice'].astype(float)
    df['Exchange'] = exchange
    df['Account'] = 'USDT-M'
    df['Leverage'] = df['leverage']
    df['MarkPrice'] = df['markPrice']
    df['LiqPrice'] = df['liquidationPrice']
    df['UnrealisedProfit'] = df['unRealizedProfit']
    df['LiqRisk'] = df.apply(calculate_value, axis=1)
    df['MaintMargin'] = df.apply(lambda row: maint_value(api_key, api_secret), axis=1)
    df =df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account', 'Leverage', 'MarkPrice', 'LiqPrice', 'LiqRisk', 'MaintMargin', 'UnrealisedProfit']]
    return df

def isolate_coin(row):
    try:
        return row['symbol'].split("_")[0][:-4]
    except:
        return row['symbol'][:-4]

def get_coinM_pos(api_key, api_secret, exchange):
    coinMPos = binance_send_signed_request("https://dapi.binance.com", 'GET', '/dapi/v1/positionRisk', api_key, api_secret, payload={})
    df = pd.DataFrame(coinMPos)
    df = df[df['positionAmt'].astype(float) != 0]
    #df['Coin'] = df['symbol'].str[:-8]
    df['Coin'] = df.apply(get_coin, axis=1)
    df['Contract'] = df['symbol']
    df['QTY'] = df['notionalValue'].astype(float)
    df['USDValue'] = df['QTY'].astype(float) * df['markPrice'].astype(float)
    df['Exchange'] = exchange
    df['Account'] = 'COIN-M'
    df['Leverage'] = df['leverage']
    df['MarkPrice'] = df['markPrice']
    df['LiqPrice'] = df['liquidationPrice']
    df['LiqRisk'] = df.apply(calculate_value, axis=1)
    df['MaintMargin'] = 0
    df =df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account', 'Leverage', 'MarkPrice', 'LiqPrice', 'LiqRisk', 'MaintMargin']]
    return df

def get_coin(row):
    if str(row['symbol']) == 'nan':
        return 'a'
    rowAlt = row['symbol'][:-8]
    if rowAlt == 'DOTUS':
        rowAlt = rowAlt[:-2]
    elif rowAlt == 'ETHUS':
        rowAlt = rowAlt[:-2]
    elif rowAlt == 'BTCUS':
        rowAlt = rowAlt[:-2]
    elif rowAlt == 'XRPUS':
        rowAlt = rowAlt[:-2]
    elif rowAlt == 'SOLUS':
        rowAlt = rowAlt[:-2]
    return rowAlt

def all_positions(api_key, api_secret, exchange):
    try:
        df = pd.concat([get_coinM_pos(api_key, api_secret, exchange), get_usdt_pos(api_key, api_secret, exchange)], ignore_index=True)
    except:
        try:
            df = get_coinM_pos(api_key, api_secret, exchange)
        except:
            try:
                df = get_usdt_pos(api_key, api_secret, exchange)
            except:
                df = pd.DataFrame()
    return df

