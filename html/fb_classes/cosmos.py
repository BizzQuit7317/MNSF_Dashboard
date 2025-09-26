import re
import requests
import numpy as np
import pandas as pd

base_urls = {'ATOM':"https://cosmos-lcd.quickapi.com:443",  #'ATOM': 'https://api.cosmos.interbloc.org',
             'KAVA': 'https://api.data.kava.io',
             'SECRET': 'https://secret-4.api.trivium.network:1317'}
'''
a cosmos validator node has a normal address and a "valoper address". to get staking info you need the valoper address.
below an example of how to build the dictionary of valoper addresses from a list of normal addresses
that will be used in the class:
'''

cosmos_valoper_addresses = {'cosmos1vzwe79zdjelepczsktulndgcfc6nug3gfq6u5z': 'cosmosvaloper18s3k8dt73e28rraqk70u9xwtv9wlav83n5mqjx', 'kava1m5twqktzu626n8g7ppfl7d9kax50hqmyg93tnw': 'kavavaloper122lg7yuwc9p9uwkfqef7wrh5uydp7q6juulfrw', 'secret1m5twqktzu626n8g7ppfl7d9kax50hqmyk43lc4': 'secretvaloper1p7hzp7y50l9f7jl3yv6cdd95a3hc2dfrqfncpt'}

cosmos_providers = {'ATOM': ['http://162.55.155.35:1317', 'https://cosmos-lcd.quickapi.com:443',
                             'https://lcd-cosmoshub.blockapsis.com', 'https://api.cosmos.interbloc.org',
                             'https://api.cosmos.network'],
                    'KAVA': ['https://api.data.kava.io/', 'https://kava-api.polkachu.com'],
                    'SCRT': ['grpc+http://162.19.72.187:9090', 'https://secret-4.api.trivium.network:1317']}
cosmos_coin_names = {'cosmos': 'ATOM',
                     'atom': 'ATOM',
                     'kava': 'KAVA',
                     'secret': 'SCRT'}

def get_binance_current_priceCOSM(coin):
    r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT").json()
    return float(r['price'])

def get_binance_price_at_timeCOSM(time, coin, margin):
    return 1

## BALANCE FUNCTIONS
class CosmosNodesAnalytics():
    '''
    Class for downloading info from Cosmos node
    '''
    def __init__(self, address, valoper_address=''):
        name = re.split(r'(\d+)', address)[0]
        self.address = address
        self.valoper_address = valoper_address
        self.coin = cosmos_coin_names[name]
        url = search_available_cosmos_provider(self.coin)
        if url:
            self.base_url = url
        else:
            raise ValueError('No available API URL found for this coin.')

    def get_total_balance(self):
        self.delegated = self.get_delegated_balance()
        self.available = self.get_available_balance()
        self.rewards = self.get_delegator_rewards()
        self.unbonding = self.get_delegator_unbonding_balance()
        self.total_balance = self.available + self.delegated + self.rewards + self.unbonding
        if len(self.valoper_address)>0:
            self.commissions = self.get_validator_commissions()
            self.total_balance += self.commissions
        return self.total_balance

    def get_total_balance_usdt(self):
        self.get_total_balance()
        self.price = get_binance_current_priceCOSM(self.coin)
        self.total_balance_usdt = self.total_balance * self.price
        self.delegated_usdt = self.delegated * self.price
        self.available_usdt = self.available * self.price
        self.unbonding_usdt = self.unbonding * self.price
        self.rewards_usdt = self.rewards * self.price
        if len(self.valoper_address)>0:
            self.commissions_usdt = self.commissions * self.price
        return self.total_balance_usdt

    def get_total_balance_kava(self):
        self.delegated = self.get_delegated_balance_kava()
        self.available = self.get_available_balance_kava()
        #self.rewards = self.get_delegator_rewards_kava()
        self.unbonding = self.get_delegator_unbonding_balance_kava()
        self.total_balance = self.unbonding + self.available + self.delegated
        return self.total_balance

    def get_total_balance_kava_usdt(self):
        self.price = get_binance_current_priceCOSM(self.coin)
        self.total_balance_usdt = self.total_balance * self.price
        return self.total_balance_usdt

    def get_delegated_balance(self):
        '''
        downloads delegated (to, not received) balance of a given wallet
        :return: balance
        '''
        #endpoint = '/staking/delegators/{}/delegations'.format(self.address)
        endpoint = '/cosmos/staking/v1beta1/delegations/{}'.format(self.address)
        url = self.base_url + endpoint
        response = requests.get(url.format(self.address))
        r = response.json()
        bal = 0
        for i in r['delegation_responses']:
            if i['balance']['denom'] in ['uatom', 'uscrt']:
                bal = int(i['balance']['amount']) / 1000000
        return bal

    def get_delegated_balance_kava(self):
        endpoint = f'/kava/liquid/v1beta1/delegated_balance/{self.address}'
        url = self.base_url + endpoint
        response = requests.get(url.format(self.address))
        r = response.json()
        return float(r['vesting']['amount']) / 1000000

    def get_available_balance_kava(self):
        endpoint = f"/cosmos/bank/v1beta1/balances/{self.address}"
        url = self.base_url + endpoint
        response = requests.get(url.format(self.address))
        r = response.json()
        return float(r['balances'][0]['amount']) / 1000000

    def get_delegator_unbonding_balance_kava(self):
        endpoint = f"/kava/liquid/v1beta1/delegated_balance/{self.address}"
        url = self.base_url + endpoint
        response = requests.get(url)
        r = response.json()
        return float(r['vested']['amount']) / 1000000

    def get_delegator_rewards_kava(self):
        endpoint = '/cosmos/distribution/v1beta1/delegators/{}/rewards'.format(self.address)
        url = self.base_url + endpoint
        response = requests.get(url)
        r = response.json()
        return r

    def get_available_balance(self):
        endpoint = '/cosmos/bank/v1beta1/balances/{}'.format(self.address)
        #endpoint = "/bank/balances/" + self.address
        url = self.base_url + endpoint
        response = requests.get(url.format(self.address))
        r = response.json()
        bal = 0
        for i in r['balances']:
            if i['denom'] in ['uatom', 'uscrt']:
                bal = float(i['amount']) / 1000000
        return bal

    def get_delegator_unbonding_balance(self):
        endpoint = '/cosmos/staking/v1beta1/delegators/{}/unbonding_delegations'.format(self.address)
        url = self.base_url + endpoint
        response = requests.get(url)
        r = response.json()
        if len(r['unbonding_responses']) == 0:
            return 0
        else:
            unb_bal = 0
            for i in r['unbonding_responses'][0]['entries']:
                unb_bal += float(i['balance']) / 1000000
            return unb_bal

    def get_delegator_rewards(self):
        endpoint = '/cosmos/distribution/v1beta1/delegators/{}/rewards'.format(self.address)
        url = self.base_url + endpoint
        response = requests.get(url)
        r = response.json()
        rew = 0
        unames = ['uscrt', 'uatom']
        if len(r['total'])>0:
            for i in r['total']:
                if i['denom'] in unames:
                    rew += float(i['amount'])
        return rew / 1000000

    def get_received_delegations(self):
        '''
        downloads received delegated balance of a given wallet
        :return: balance
        '''
        if len(self.valoper_address) > 0:
            endpoint = '/cosmos/staking/v1beta1/validators/{}/delegations'.format(self.valoper_address)
            url = self.base_url + endpoint
            response = requests.get(url)
            r = response.json()
            df = pd.DataFrame(columns=['delegator_address', 'qty'])
            count = 0
            for i in r['delegation_responses']:
                diz = i['delegation']
                df.loc[count] = [diz['delegator_address'], float(diz['shares']) / 1000000]
                count += 1
            return df
        else:
            print('This address is not of a staking wallet.')

    def get_validator_commissions(self):
        if len(self.valoper_address) > 0:
            endpoint = '/cosmos/distribution/v1beta1/validators/{}/commission'.format(self.valoper_address)
            url = self.base_url + endpoint
            response = requests.get(url)
            r = response.json()
            try:
                comms = 0
                for i in r['commission']['commission']:
                    if (i['denom'] == 'uatom') or (i['denom'] == 'uscrt'):
                        comms += float(i['amount']) / 10 ** 6
            except:
                comms = 0
            return comms
        else:
            print('Missing validator address.')

    def get_outstanding_rewards(self):
        '''
        All rewards of a validator (also delegators rewards)
        '''
        if len(self.valoper_address) > 0:
            endpoint = '/cosmos/distribution/v1beta1/validators/{}/outstanding_rewards'.format(self.valoper_address)
            url = self.base_url + endpoint
            response = requests.get(url)
            r = response.json()
            out = r['rewards']['rewards'][0]['amount']
            return float(out)/ 1000000
        else:
            print('This address is not of a staking wallet.')

    def download_cosmos_transactions(self):
        endpoint = '/cosmos/tx/v1beta1/txs'
        url = self.base_url + endpoint
        event_types = ["message.sender='{}'".format(self.address),
                       "transfer.recipient='{}'".format(self.address)]
        df = pd.DataFrame(columns=['datetime', 'type', 'amount', 'fee', 'sender', 'receiver', 'tx_hash'])
        for ev in event_types:
            params = {
                "events": ev
            }
            response = requests.get(url, params=params)
            r = response.json()
            temp = self._manage_transactions_output(r)
            df = pd.concat([df, temp], ignore_index=True)
        df.sort_values('datetime', inplace=True)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def _manage_transactions_output(self, r):
        df = pd.DataFrame(columns=['datetime', 'type', 'amount', 'fee', 'sender', 'receiver', 'tx_hash'])
        for i in range(len(r['txs'])):
            if len(r['tx_responses'][i]['data'])==0:
                continue
            trans_type_raw = r['txs'][i]['body']['messages'][0]['@type']
            temp_diz = r['txs'][i]['body']['messages'][0]
            if 'MsgSend' in trans_type_raw:
                sender_address = temp_diz['from_address']
                receiver_address = temp_diz['to_address']
                amount = float(temp_diz['amount'][0]['amount'])/1000000
                if sender_address == self.address:
                    trans_type = 'SendTokens'
                else:
                    trans_type = 'ReceiveTokens'
            elif 'MsgCreateValidator' in trans_type_raw:
                trans_type = 'CreateValidator'
                sender_address = temp_diz['delegator_address']
                receiver_address = temp_diz['validator_address']
                amount = float(temp_diz['value']['amount'])/1000000
            elif 'MsgWithdrawDelegatorReward' in trans_type_raw:
                trans_type = 'WithdrawDelegatorReward'
                sender_address = temp_diz['validator_address']
                receiver_address = temp_diz['delegator_address']
                if 'uatom' in r['tx_responses'][i]['raw_log']:
                    try:
                        amount = int(r['tx_responses'][i]['raw_log'].split('uatom')[-1].split(',')[-1])/ 1000000
                    except:
                        amount = int(r['tx_responses'][i]['raw_log'].split('uatom')[-2].split(',')[-1])/ 1000000
                elif 'ukava' in r['tx_responses'][i]['raw_log']:
                    try:
                        amount = int(r['tx_responses'][i]['raw_log'].split('ukava')[-1].split('"')[-1])/ 1000000
                    except:
                        amount = int(r['tx_responses'][i]['raw_log'].split('ukava')[-2].split('"')[-1]) / 1000000
                elif 'uscrt' in r['tx_responses'][i]['raw_log']:
                    try:
                        amount = int(r['tx_responses'][i]['raw_log'].split('uscrt')[-1].split(',')[-1])/ 1000000
                    except:
                        amount = int(r['tx_responses'][i]['raw_log'].split('uscrt')[-2].split(',')[-1]) / 1000000
                else:
                    amount = 0
            elif 'MsgDelegate' in trans_type_raw:
                trans_type = 'Delegate'
                sender_address = temp_diz['delegator_address']
                receiver_address = temp_diz['validator_address']
                amount = float(temp_diz['amount']['amount']) / 1000000
            elif 'MsgVote' in trans_type_raw:
                trans_type = 'Vote'
                sender_address = temp_diz['voter']
                receiver_address = np.nan
                amount = np.nan
            elif 'MsgUndelegate' in trans_type_raw:
                trans_type = 'Undelegate'
                sender_address = temp_diz['validator_address']
                receiver_address = temp_diz['delegator_address']
                amount = float(temp_diz['amount']['amount']) / 1000000
            elif 'MsgMultiSend' in trans_type_raw:
                trans_type = 'MultiSend'
                sender_address = temp_diz['inputs'][0]['address']
                receiver_address = temp_diz['outputs'][0]['address']
                amount = float(temp_diz['inputs'][0]['coins'][0]['amount']) / 1000000
            elif 'MsgExec' in trans_type_raw:
                if 'MsgVote' in temp_diz['msgs'][0]['@type']:
                    sender_address = temp_diz['msgs'][0]['voter']
                    receiver_address = np.nan
                    amount = np.nan
                    trans_type = 'Vote'
                elif 'MsgDelegate' in temp_diz['msgs'][0]['@type']:
                    sender_address = temp_diz['msgs'][0]['validator_address']
                    receiver_address = self.address
                    amount = 0
                    for k in temp_diz['msgs']:
                        if k['delegator_address'] == self.address:
                            amount += float(k['amount']['amount']) / 1000000
                    trans_type = 'auto_restake'
                else:
                    print('Unknown transaction type')
                    continue
            elif 'MsgEditValidator' in trans_type_raw:
                receiver_address = temp_diz['validator_address']
                sender_address = ''
                amount = 0
                trans_type = 'EditValidator'
            else:
                print('Unknown transaction type.')
                trans_type = 'Unknown'
                sender_address = ''
                receiver_address = ''
                amount = 0
            tx_hash = r['tx_responses'][i]['txhash']
            ts = r['tx_responses'][i]['timestamp'].replace('T', ' ').replace('Z', '')
            fee = int(r['txs'][i]['auth_info']['fee']['amount'][0]['amount'])/1000000
            df.loc[i] = [ts, trans_type, float(amount), fee, sender_address, receiver_address, tx_hash]
        return df

    def add_prices_to_txs_dataframe(self, df):
        prs = []
        for i, r in df.iterrows():
            if (r['type'] == 'ReceiveTokens') or (r['type'] == 'SendTokens'):
                pr = get_binance_price_at_timeCOSM(r['datetime'], self.coin, 'USDT')
                prs.append(pr)
            else:
                prs.append(np.nan)
        df.insert(2, 'price', prs)
        return df


def search_available_cosmos_provider(coin):
    """
    This method searches for a working Cosmos API URL.
    """
    header = {"Content-Type": "application/json"}
    endpoint = '/cosmos/base/tendermint/v1beta1/blocks/latest'
    for base_url in cosmos_providers[coin]:
        url = base_url.replace('grpc+', '').replace('9090', '1317')
        try:
            r = requests.get(url + endpoint, headers=header, timeout=5).json()
            return base_url
        except:
            pass
    return None


def get_cosmos_delegator_balance(address):
    '''
    This method returns the balance of a given Cosmos delegator address
    :param address: address
    :return: balance
    '''
    cl = CosmosNodesAnalytics(address)
    cl.get_total_balance_usdt()
    res = {'available': cl.available, 'delegated': cl.delegated, 'rewards_to_claim': cl.rewards,
           'unbonding': cl.unbonding, 'total_balance': cl.total_balance, 'price': cl.price}
    return res
