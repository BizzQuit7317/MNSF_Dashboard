import requests
import base58
import hashlib
import pandas as pd
import numpy as np

view_base_url_mainnet = 'https://api.avax.network/ext/bc/'

class AvaxNodesAnalytics():
    def __init__(self, address_p, address_hex):
        self.address_p = address_p
        self.address_hex = address_hex
        self.base_url = 'http://141.95.100.75:8081'

    def get_total_balance(self):
        c_bal = self.get_c_chain_balance()
        c2p = self.get_utxos_on_chain('c')
        p = self.get_utxos_on_chain('p')
        p2c = self.get_utxos_moving('c')
        staked = self.get_staked_balances()

        c2p_bal = c2p['amount'].sum()/10**9
        p_bal = p['amount'].sum()/10**9
        p2c_bal = p2c['amount'].sum()/10**9
        staked_bal = staked['amount'].sum()/10**9
        available = c_bal + c2p_bal + p_bal + p2c_bal
        total_bal = available + staked_bal
        res = {'total': total_bal, 'C': c_bal, 'C2P': c2p_bal, 'P': p_bal, 'P2C': p2c_bal, 'staked': staked_bal}
        return res

    def get_c_chain_balance(self):
        ## needs review when more utxos are available
        endpoint = '/account/balance'
        url = self.base_url + endpoint
        params = self._build_network_identifier('c')
        params["account_identifier"] = {"address": self.address_hex}
        params["include_mempool"] = False
        response = requests.post(url, json=params)
        r = response.json()
        bal = int(r['balances'][0]['value']) / 10 ** 18
        return bal

    def get_utxos_on_chain(self, chain):
        url = 'https://api.avax.network/ext/bc/P' # TESTNET URL. WILL CHANGE TO MAINNET

        params = {"jsonrpc": "2.0", "id": 1, "method": "platform.getUTXOs",
                  "params": {"addresses": [self.address_p],
                "sourceChain": chain.upper(), "encoding": "hex"}}
        response = requests.post(url, json=params)
        r = response.json()
        df = pd.DataFrame(columns=['output_index', 'amount', 'tx_id'])
        count=0
        for hex_string in r['result']['utxos']:
            res = self._decode_utxo_hex(hex_string)
            df.loc[count] = [res['output_index'], res['amount'], res['tx_id']]
            count += 1
        return df

    def get_utxos_moving(self, chain):
        url = 'https://api.avax.network/ext/bc/C/avax'

        params = {"jsonrpc": "2.0", "id": 1, "method": "avax.getUTXOs",
                  "params": {"addresses": [self.address_p.replace('P', 'C')],
                             "sourceChain": chain.upper(), "encoding": "hex"}}
        response = requests.post(url, json=params)
        r = response.json()
        df = pd.DataFrame(columns=['output_index', 'amount', 'tx_id'])
        count = 0
        for hex_string in r['result']['utxos']:
            res = self._decode_utxo_hex(hex_string)
            df.loc[count] = [res['output_index'], res['amount'], res['tx_id']]
            count += 1
        return df

    def get_staked_balances(self):
        url = 'https://api.avax.network/ext/bc/P'

        params = {"jsonrpc": "2.0", "id": 1, "method": "platform.getStake",
                  "params": {"addresses": [self.address_p], "encoding": "hex"}}
        response = requests.post(url, json=params)
        r = response.json()
        df = pd.DataFrame(columns=['id', 'amount', 'tx_id'])
        count = 0
        for i in r['result']['stakedOutputs']:
            res = self._decode_staking_utxo_hex(i)
            df.loc[count] = [res['id'], res['amount'], res['tx_id']]
            count += 1
        return df

    def _decode_utxo_hex(self, hex_string):
        id = int(hex_string[2:6], 16)
        # Decode the next 32 bytes using base58_check
        tx_id = base58.b58encode(add_checksum(bytes.fromhex(hex_string[6:70]))).decode()
        # Decode the next 4 bytes as an integer
        output_index = int(hex_string[70:78], 16)
        # Decode the next 32 bytes as a hex string
        asset_id = base58.b58encode(add_checksum(bytes.fromhex(hex_string[78:142]))).decode()
        output = hex_string[142:]
        # Decode the remainder of the string using the specified rules
        output_id = int(output[:8], 16)
        amount = int(output[8:24], 16)
        #amount = amount / 10 ** 9
        locktime = int(output[24:40], 16)
        threshold = int(output[40:48], 16)
        address_length = int(output[48:56], 16)
        address = output[56:96]
        res = {'id': id, 'tx_id': tx_id, 'output_index': output_index, 'asset_id': asset_id, 'output_id': output_id,
                'amount': amount, 'locktime': locktime, 'threshold': threshold, 'address_length': address_length,
                'address': address}
        return res

    def _decode_staking_utxo_hex(self, hex_string):
        id = int(hex_string[2:6], 16)
        tx_id = base58.b58encode(add_checksum(bytes.fromhex(hex_string[6:70]))).decode()
        output = hex_string[70:]
        # Decode the remainder of the string using the specified rules
        output_id = int(output[:8], 16)
        amount = int(output[8:24], 16)
        #amount = amount/10**9
        locktime = int(output[24:40], 16)
        threshold = int(output[40:48], 16)
        address_length = int(output[48:56], 16)
        address = output[56:96]
        res = {'id': id, 'tx_id': tx_id, 'output_id': output_id,
                'amount': amount, 'locktime': locktime, 'threshold': threshold, 'address_length': address_length,
                'address': address}
        return res

    def _build_network_identifier(self, chain):
        if chain.lower() == 'p':
            num = 1
        elif chain.lower() == 'c':
            num = 0
        else:
            raise ValueError('chain must be either "p" or "c"')
        params = {'network_identifier': self._get_network_identifier()['network_identifiers'][num]}
        return params

    def _get_network_identifier(self):
        endpoint = '/network/list'
        prms = {'metadata': {}}
        r = self.send_rosetta_request(endpoint, prms)
        return r

    def send_rosetta_request(self, endpoint, params):
        url = self.base_url + endpoint
        response = requests.post(url, json=params)
        r = response.json()
        return r


def get_avax_delegator_balance(address_p, address_hex):
    pr = get_binance_current_priceCOSM('AVAX')
    ax = AvaxNodesAnalytics(address_p, address_hex)
    bal = ax.get_total_balance()
    available = bal['total'] - bal['staked']
    res = {'available': available, 'delegated': bal['staked'], 'rewards_to_claim': np.nan,
           'unbonding': 0, 'total_balance': bal['total'], 'price': pr}
    return res

def get_avax_validator_info(validator_address):
    url = view_base_url_mainnet + 'P'
    params = {"jsonrpc": "2.0", "id": 1, "method": "platform.getCurrentValidators",
              "params": {
    "subnetID": "11111111111111111111111111111111LpoYY",
    "nodeIDs": [validator_address]}}
    response = requests.post(url, json=params)
    r = response.json()
    return r['result']['validators'][0]

def get_avax_validator_info_for_stakingRewards(node_id):
    t = get_avax_validator_info(node_id)
    pr = get_binance_current_priceCOSM('AVAX')
    bal = int(t['stakeAmount'])/10**9
    res = {'tokenBalance': bal, 'balanceUsd': bal*pr, 'users': int(t['delegatorCount']), 'fee': 0.1}
    return res


def add_checksum(buff):
    hash_obj = hashlib.sha256()
    hash_obj.update(buff)
    hashed = hash_obj.digest()
    checksum = hashed[-4:]
    return buff + checksum

def get_binance_current_priceCOSM(coin):
    r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT").json()
    return float(r['price'])