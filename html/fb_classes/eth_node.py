from web3 import Web3
import requests


class EthNodesAnalytics:
    """
    Class for monitoring ETH assets
    """
    def __init__(self, address, testnet=False):
        self.address = address
        if testnet:
            self.base_url = 'https://holesky.infura.io/v3/aaa403aaa21a42758699d70f75d827f5'
            self.beacon_url = ''
        else:
            self.base_url = 'https://mainnet.infura.io/v3/aaa403aaa21a42758699d70f75d827f5'
            self.beacon_url = 'https://beaconcha.in/api/v1/'
        self.params = {"id": "1",
                       "jsonrpc": "2.0"}
        self.w3 = Web3(Web3.HTTPProvider(self.base_url))

    def get_available_balance(self):
        # Get ETH balance
        balance = self.w3.eth.get_balance(self.address)
        balance = balance / 10 ** 18
        return balance

    def get_delegated_balance(self):
        delegations = self.get_delegation_overview()
        return sum(delegations.values())

    def get_delegation_overview(self):
        keys = self.get_validators_of_an_address()
        delegations = {}
        for pub_key in keys:
            endpoint = 'validator/' + pub_key + '/deposits'
            response = requests.get(self.beacon_url + endpoint)
            r = response.json()
            #print(r)
            for i in r['data']:
                delegations[pub_key] = i['amount'] / 10 ** 9
        return delegations

    def get_validators_of_an_address(self):
        not_working_keys = {}
        endpoint = 'validator/eth1/' + self.address
        response = requests.get(self.beacon_url + endpoint)
        r = response.json()
        #print(r)
        keys = []
        for i in r['data']:
            if not_working_keys[i['publickey']]:
                keys.append(i['publickey'])
        #    keys = [i['publickey'] for i in r['data']]
        #print(keys)
        return keys


