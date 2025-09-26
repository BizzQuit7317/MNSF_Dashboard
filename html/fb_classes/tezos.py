import requests
import numpy as np
import pandas as pd


def get_tezos_node_balance_history(address):
    '''
    gets historical balance at every transaction for a tezos node
    :param address: node address
    :return: transaction dataframe
    '''
    base_url = 'https://api.tzstats.com'
    endpoint = '/explorer/account/{}/operations'.format(address) + '?limit=100'
    url = base_url + endpoint
    response = requests.get(url)
    r = response.json()
    df = pd.DataFrame(columns=['date', 'type', 'height', 'cycle', 'qty', 'fee', 'id'])
    count = 0
    for i in r:
        dt = i['time'].replace('T', ' ')[:-1]
        tipo = i['type']
        if (tipo == 'reward') or (tipo == 'deposit'):
            df.loc[count] = [dt, tipo, i['height'], i['cycle'], i[tipo], np.nan, i['id']]
            count += 1
        elif (tipo == 'transaction') or (tipo == 'delegation'):
            df.loc[count] = [dt, tipo, i['height'], i['cycle'], i['volume'], i['fee'], i['id']]
            count += 1
    df.sort_values('date', inplace=True)
    pp = []
    for i, r in df.iterrows():
        if r['type'] == 'transaction':
            pr = get_binance_price_at_timeCOSM(r['date'], 'XTZ', 'USDT')
            pp.append(pr)
        else:
            pp.append(np.nan)
    df['price'] = pp
    return df

def get_tezos_node_last_balance(address):
    '''
    get last balance of a tezos node
    :param address: node address
    :return: balance
    '''
    url = 'https://api.tzkt.io/v1/accounts/' + address + '/balance'
    response = requests.get(url)
    r = response.json()
    return r / 1000000

def get_tezos_delegated_balance_on_node(address):
    url = 'https://api.tzkt.io/v1/rewards/bakers/'+address
    response = requests.get(url)
    r = response.json()
    delegated = r[0]['delegatedBalance'] / 1000000
    return delegated

def get_tezos_rewards_for_node(address):
    cycles = requests.get('https://api.tzstats.com/explorer/config/head').json()['preserved_cycles']
    url = "https://api.tzstats.com/explorer/bakers/"+address+"?meta=True"
    response = requests.get(url)
    r = response.json()['stats']['total_rewards_earned']
    result = r 
    print(result)
    return result

def get_binance_price_at_timeCOSM(time, coin, margin):
    return 1
