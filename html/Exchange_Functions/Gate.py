import pandas as pd
import time, hashlib, hmac, requests

def signature(method, url, chiave_gate, segreta_gate, query_string=None, payload_string=None):
    key = chiave_gate
    secret = segreta_gate
    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}


def send_signed_request(url, chiave_gate, segreta_gate):
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    query_param = ''
    # for `gen_sign` implementation, refer to section `Authentication` above
    sign_headers = signature('GET', prefix + url, chiave_gate, segreta_gate, query_param)
    headers.update(sign_headers)
    r = requests.request('GET', host + prefix + url, headers=headers)
    #print(r.json())
    return r.json()

def current_price(base):
    try:
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/tickers'
        query_param = 'currency_pair=' + base + '_' + 'USDT'
        r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers)
        return float(r.json()[0]['last'])
    except:
        return 1

def usdCalc(row):
    return float(row['QTY']) * current_price(row['Coin'])

def gate_swap_balance(api_key, api_secret, exchange):
    gate_wallet = send_signed_request('/unified/accounts', api_key, api_secret)
    #gate_wallet = send_signed_request('/margin/accounts', api_key, api_secret)
    #print(gate_wallet)
    try:
        df = pd.DataFrame(gate_wallet)
        #df = df[df.iloc[:, 0] != "USDT"]
        #######df = df[df.index == 'USDT']
        #print(f"{df}\n###############################1\n")
        df = df[df['balances'].apply(lambda x: x['equity']) != '0']
        #print(f"{df}\n###############################2\n")
        #df.rename(columns={'total_margin_balance': 'QTY'}, inplace=True)
        #print(len(df))
        #df['QTY'] = df['balances'][0]['equity']
        df['QTY'] = df['balances'].apply(lambda x: x['equity'])
        df['Coin'] = df.index
        df['USDValue'] = df.apply(usdCalc, axis=1)
        df['Contract'] = df['Coin']
        df['Exchange'] = exchange
        df['Account'] = 'USDT-M'
        df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]
        #print(f"{df}\n###############################3\n")
        df.reset_index(drop=True, inplace=True)
        #print(df)
        return df
    except Exception as e:
        print(f"ERROR WITH GATE SPOT WALLET: {e}")



def gate_spot_balance(api_key, api_secret, exchange):
    gate_wallet = send_signed_request('/spot/accounts', api_key, api_secret)
    try:

        df = pd.DataFrame(gate_wallet)

        if exchange == "Gate":
            df = df[df['currency'] != "USDT"]

        df = df[df.index == 'USDT']

        df = df[(df['locked'] != '0') | (df['available'] != '0')]
        df.rename(columns={'currency': 'Coin'}, inplace=True)
        df['Contract'] = df['Coin']
        df['Exchange'] = exchange
        df['Account'] = 'SPOT'
        df['QTY'] = df['available'].astype(float) + df['locked'].astype(float)
        df['USDValue'] = df.apply(lambda row: row['QTY'] * float(current_price(row['Contract'])), axis=1)
        df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]
        #print(df)
        return df
    except Exception as e:
        print(f"ERROR WITH GATE SPOT WALLET: {e}")



def gate_total_balance(api_key, api_secret, exchange):
    try:
        df = pd.concat([gate_spot_balance(api_key, api_secret, exchange), gate_swap_balance(api_key, api_secret, exchange)], axis=0)
        #df = gate_spot_balance(api_key, api_secret, exchange)
    except:
        df = gate_swap_balance(api_key, api_secret, exchange)
        #df = pd.DataFrame()
    #print(df)
    return df

def maint_value(api_key, api_secret):
    try:
        margin = send_signed_request('/unified/accounts', api_key, api_secret)["total_maintenance_margin"]
        return float(margin)
    except:
        return 0



def get_usdt_pos(api_key, api_secret, exchange):
    usdtPos = send_signed_request('/futures/usdt/positions', api_key, api_secret)
    try:
        df = pd.DataFrame(usdtPos)
        df = df[(df['size'] != '0')]
        df.rename(columns={'contract': 'Contract'}, inplace=True)
        df['Coin'] = df['Contract']
        df['Coin'] = df['Coin'].str[:-5]
        #df['QTY'] = df['value'].astype(float)/df['mark_price'].astype(float)
        df['QTY'] = (df['unrealised_pnl'].astype(float)/((df['mark_price'].astype(float)-df['entry_price'].astype(float))*df['size'].astype(float))) * df['size'].astype(float)
        df['USDValue'] = df['QTY'] * df['mark_price'].astype(float)
        df['Exchange'] = exchange
        df['Account'] = 'USDT-M'
        df.rename(columns={'cross_leverage_limit': 'Leverage'}, inplace=True)
        df.rename(columns={'mark_price': 'MarkPrice'}, inplace=True)
        df.rename(columns={'liq_price': 'LiqPrice'}, inplace=True)
        #try:
        #    df['LiqRisk'] = (df['LiqPrice'].astype(float)-df['MarkPrice'].astype(float))/df['MarkPrice'].astype(float)
        #except:
        #    df['LiqRisk'] = 1
        df['LiqRisk'] = 1
        df['MaintMargin'] = df.apply(lambda row: maint_value(api_key, api_secret), axis=1)
        df =df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account', 'Leverage', 'MarkPrice', 'LiqPrice', 'LiqRisk', 'MaintMargin']]
        df = df.dropna()
        return df
    except Exception as e:
        print(f"Gate usdt pos ERROR: {e}")
