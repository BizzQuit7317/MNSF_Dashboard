import pandas as pd
import requests, base64, hmac
from datetime import datetime
import time

def okx_get_header(endpoint, api_key, api_secret, api_pass):
    body = {}
    current_time = current_time_okx()
    header = {
        'CONTENT_TYPE':'application/json',
        'OK-ACCESS-KEY':api_key,
        'OK-ACCESS-SIGN':okx_signature(current_time, endpoint, body, api_secret),
        'OK-ACCESS-TIMESTAMP':current_time,
        'OK-ACCESS-PASSPHRASE':api_pass
    }
    return header

def okx_signature(timestamp, request_path, body, api_secret):
    if str(body) == '{}' or str(body) == 'None':
        body = ''
    message = str(timestamp) + 'GET' + request_path + str(body)
    mac = hmac.new(bytes(api_secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)

def current_time_okx():
    now = datetime.utcnow()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"

def get_okx_trading_wallet(api_key, api_secret, api_pass):
    ## Trading wallet
    url = '/api/v5/account/balance'
    header = okx_get_header(url, api_key, api_secret, api_pass)
    response = requests.get('http://www.okx.com' + url, headers=header)
    #response = requests.get('http://www.okex.com' + url, headers=header)
    r = response.json()
    return r

def get_okx_funding_wallet(api_key, api_secret, api_pass):
    url = '/api/v5/asset/balances'
    header = okx_get_header(url, api_key, api_secret, api_pass)
    response = requests.get('http://www.okx.com' + url, headers=header)
    #response = requests.get('http://www.okex.com' + url, headers=header)
    r = response.json()
    #print('\n############\n', r, '\n~~~\n', response, '\n###############\n')
    w = pd.DataFrame(columns=['Qty', 'USDValue'])
    return r


def okx_send_unsigned_request(url_path, payload={}):
    BASE_URL = 'https://www.okx.com'
    url = BASE_URL + url_path
    response = requests.get(url)
    return response.json()

def get_okx_current_price(base, quote):
    res = okx_send_unsigned_request("/api/v5/market/ticker?instId=" + base+'-'+quote, payload={})
    return float(res['data'][0]['last'])

def get_loans(api_key, api_secret, api_pass):
    try:
        loan_types = ['212', '215', '217', '218', '231', '176']

        url = '/api/v5/asset/bills'
        header = okx_get_header(url, api_key, api_secret, api_pass)
        response = requests.get('http://www.okx.com' + url, headers=header)
        df = pd.DataFrame(response.json()['data'])

        df = df[df['type'].isin(loan_types)] #remove all non loan types
        df['balChg'] = df['balChg'].astype(float) * -1 #invert all balance change values

        df = df.rename(columns={"ccy":"Coin", "balChg":"QTY"})
        df['Contract'] = df['Coin']
        df['USDValue'] = df.apply(get_prices, axis=1)
        df['Exchange'] = "Okx_Loan"
        df['Account'] = "Loan"

        df = df[["Coin", "Contract", "QTY", "USDValue", "Exchange", "Account"]]
    except:
        df = pd.DataFrame()
    return df

def get_prices(row):
    try:
        return float(row['QTY']) * get_okx_current_price(row['Coin'], "USDT")
    except Exception as e:
        print(e)
        return row['QTY']

def get_loan_info(api_key, api_secret, api_pass):
    url = '/api/v5/finance/flexible-loan/loan-info'
    header = okx_get_header(url, api_key, api_secret, api_pass)
    x = requests.get('http://www.okx.com' + url, headers=header).json()

    Loan_Amount = x['data'][0]["loanData"][0]['amt']
    Collateral = x['data'][0]['collateralNotionalUsd']
    currentLTV = x['data'][0]['curLTV']
    Margin_Call_LTV = x['data'][0]['marginCallLTV']
    Liquidation_LTV = x['data'][0]['liqLTV']
    Liquidation_Price = x['data'][0]['riskWarningData']['liqPx']

    y = {"Loan Amount":Loan_Amount, "Collateral":Collateral, "Current LTV":currentLTV, "Margin Call LTV":Margin_Call_LTV, "Liquidation LTV":Liquidation_LTV, "Liquidation Price":Liquidation_Price}


    return [y]

def trying():
    url = '/api/v5/finance/staking-defi/orders-active'
    header = okx_get_header(url, 'b31868f6-5da1-4632-807a-5c11461fb885', 'DBE05EDEF38A320C9DBE64CD91BFE651', 'qju2wgy6dkqRZM7qyt')
    #response = requests.get('http://www.okex.com' + url, headers=header)
    response = requests.get('http://www.okx.com' + url, headers=header)
    r = response.json()
    w = pd.DataFrame(columns=['Qty', 'USDValue'])
    return response

#old replaced with function same name below okx_wallet_total
#def speed_balance(api_key, api_secret, api_pass):
#    url = "/api/v5/account/balance"
#    header = okx_get_header(url, api_key, api_secret, api_pass)
#    #r = requests.get('http://www.okex.com' + url, headers=header).json()
#    r = requests.get('http://www.okx.com' + url, headers=header).json()
#    return r['data'][0]['adjEq']

def get_positions(api_key, api_secret, api_pass):
    url = '/api/v5/account/positions'
    header = okx_get_header(url, api_key, api_secret, api_pass)
    #response = requests.get('http://www.okex.com' + url, headers=header)
    response = requests.get('http://www.okx.com' + url, headers=header)
    r = response.json()
    return r

def get_contract(api_key, api_secret, api_pass, instType):
    url = '/api/v5/public/instruments?instType='+instType
    header = okx_get_header(url, api_key, api_secret, api_pass)
    #response = requests.get('http://www.okex.com' + url, headers=header)
    response = requests.get('http://www.okx.com' + url, headers=header)
    r = response.json()
    return r

def get_earn(api_key, api_secret, api_pass):
    url = '/api/v5/finance/staking-defi/orders-active'
    #url = '/api/v5/asset/saving-balance'
    header = okx_get_header(url, api_key, api_secret, api_pass)
    #response = requests.get('http://www.okex.com' + url, headers=header)
    response = requests.get('http://www.okx.com' + url, headers=header)
    r = response.json()
    return r

def get_data(url, api_key, api_secret, api_pass):
    header = okx_get_header(url, api_key, api_secret, api_pass)
    #response = requests.get('http://www.okex.com' + url, headers=header)
    response = requests.get('http://www.okx.com' + url, headers=header)
    r = response.json()
    return r

def addCustomCoin(symb, qty):
    try:
        coin_price = get_okx_current_price(symb, 'USDT')
        USD_Value = float(qty)*float(coin_price)
        values = {'coinP':float(coin_price), 'USD':float(USD_Value), 'Coin':symb, 'qty':float(qty)}
        return values
    except:
        print('Invalid coin symbol')

def get_price_standard(row):
    try:
        return  float(row['QTY']) * float(get_okx_current_price(row['Contract'], 'USDT'))
    except Exception as e:
        print(f"Error getting price for {row['Coin']}: {e}")
        return row['QTY']

def standardFraming(data, balance, qtyFlag, qty, usdFlag, exchange, account):
    df = pd.DataFrame(data)
    df.rename(columns={balance: 'Coin'}, inplace=True)
    df['Contract'] = df['Coin']
    if qtyFlag:
        df['QTY'] = df.apply(qtyCheck, axis=1)
    else:
        df['QTY'] = df[qty]
    if usdFlag:
        df['USDValue'] = df['eqUsd']
    else:
        df['USDValue'] = df.apply(get_price_standard, axis=1)
        #try:
        #    df['USDValue'] = df.apply(lambda row: float(row['QTY']) * float(get_okx_current_price(row['Contract'], 'USDT')), axis=1)
        #except:
        #    df['USDValue'] = df.apply(lambda row: row['QTY'], axis=1)
    df['Exchange'] = exchange
    df['Account'] = account
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]

    return df

def qtyCheck(row):
    if row['protocolType'] == 'defi':
        return float(row['investData'][0]['amt']) + float(row['earningData'][0]['earnings'])
    else:
        return float(row['investData'][0]['amt'])

def okx_funding_wallet_balance(api_key, api_secret, api_pass, exchange):
    funding_wallet = get_okx_funding_wallet(api_key, api_secret, api_pass)
    try:
        df = standardFraming(funding_wallet['data'], 'ccy', False, 'bal', False, exchange, 'SPOT')
        df = df[df['QTY'].astype(float) >= 0.005]
        return df
    except Exception as e:
        print('ERROR WITH FUNDING WALLET OKX:     '+str(e))
        return pd.DataFrame()

#okx_funding_wallet_balance('3ecc9f06-db1c-4ebf-9778-743a8c31e2c7', '1E40E12CAC5B1547113A524B6659F79B', 'JAKjHG6N!RfFYT6tNgiJ7', 'exchange')

def okx_trading_wallet_balance(api_key, api_secret, api_pass, exchange):
    trading_wallet = get_okx_trading_wallet(api_key, api_secret, api_pass)
    try:
        df = standardFraming(trading_wallet['data'][0]['details'], 'ccy', False, 'cashBal', True, exchange, 'USDT-M')
        return df
    except Exception as e:
        print('ERROR WITH TRADING WALLET OKX:     '+str(e))
        return pd.DataFrame()

def get_earn_balance(api_key, api_secret, api_pass, exchange):
    earn_wallet = get_earn(api_key, api_secret, api_pass)
    try:
        df = standardFraming(earn_wallet['data'], 'ccy', True, 'amt', False, exchange, 'Earn')
        
        return df
    except Exception as e:
        print('ERROR WITH EARN WALLET OKX:     '+str(e))
        return pd.DataFrame()

def okx_wallet_total(api_key, api_secret, api_pass, exchange):
    try:
        df = pd.concat([get_earn_balance(api_key, api_secret, api_pass, exchange), okx_trading_wallet_balance(api_key, api_secret, api_pass, exchange), okx_funding_wallet_balance(api_key, api_secret, api_pass, exchange)], ignore_index=True)
        return df
    except:
        return pd.DataFrame()

def speed_balance(api_key, api_secret, api_pass):
    try:
        total = okx_wallet_total(api_key, api_secret, api_pass, "Okx")
        return total['USDValue'].astype(float).sum()
    except:
        return 0

def maint_value(api_key, api_secret, api_pass):
    r = get_okx_trading_wallet(api_key, api_secret, api_pass)
    return r['data'][0]['mmr']

def strip_swap(row):
    try:
        return row['instId'].split("-")[0]
    except:
        return row['instId']

def get_usdt_pos(api_key, api_secret, api_pass, exchange):
    usdtPos = get_positions(api_key, api_secret, api_pass)
    contract_size = get_contract(api_key, api_secret, api_pass, 'SWAP')
    try:
        df = pd.DataFrame(usdtPos['data'])
        df =df[['instId', 'lever', 'markPx', 'liqPx', 'pos']]
        dfx = pd.DataFrame(contract_size['data'])
        dfx =dfx[['instId', 'ctVal']]
        instId_values = df['instId'].unique()
        dfx = dfx[dfx['instId'].isin(instId_values)]
        df = df.merge(dfx, on='instId', how='inner')
        df['Contract'] = df['instId']
        df['instId'] = df.apply(strip_swap, axis=1)
        df['Exchange'] = exchange
        df['Account'] = 'USDT-M'
        df['QTY'] = df['ctVal'].astype(float) * df['pos'].astype(float)
        df['USDValue'] = df['QTY'].astype(float) * df['markPx'].astype(float)
        try:
            df['LiqRisk'] = (df['liqPx'].astype(float)-df['markPx'].astype(float))/df['markPx'].astype(float)
        except:
            df['LiqRisk'] = 1
            df['liqPx'] = 0
        df.rename(columns={'instId': 'Coin'}, inplace=True)
        df.rename(columns={'lever': 'Leverage'}, inplace=True)
        df.rename(columns={'markPx': 'MarkPrice'}, inplace=True)
        df.rename(columns={'liqPx': 'LiqPrice'}, inplace=True)
        df['MaintMargin'] = df.apply(lambda row: maint_value(api_key, api_secret, api_pass), axis=1)
        df =df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account', 'Leverage', 'MarkPrice', 'LiqPrice', 'LiqRisk', 'MaintMargin']]
        return df
    except Exception as e:
        print('ERROR WITH USDTPOS WALLET OKX:     '+str(e))


