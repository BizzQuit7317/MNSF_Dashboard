import base64, json, requests
import numpy as np

class NearNodesAnalytics():
    """
    Class for monitoring Near assets
    """

    def __init__(self, address, validator_address='colossus.poolv1.near'):
        self.address = address
        self.validator_address = validator_address
        self.base_url = 'http://rosetta-near-mainnet.colossus.life:3040'
        self.view_base_url = 'https://rpc.mainnet.near.org'
        self.params = {}

    def get_account_total_balance(self):
        available = self.get_account_available_balance()
        try:
            staked = self.get_account_staked_balance()
        except:
            staked = 0
        try:
            unstaked = self.get_account_unstaked_balance()
        except:
            unstaked = 0
        total = available + staked + unstaked
        res = {'total': total, 'available': available, 'staked': staked, 'unstaked': unstaked}
        return res

    def get_account_available_balance(self):
        params = self._build_network_identifier()
        params['account_identifier'] = {'address': self.address}
        endpoint = '/account/balance'
        r = self.send_rosetta_request(endpoint, params)
        return int(r['balances'][0]['value'])/10**24

    def get_account_staked_balance(self):
        s = '{"account_id": "'+self.address+'"}'
        b64_encoded = base64.b64encode(s.encode())
        encoded_args = b64_encoded.decode()
        params = {
            "jsonrpc": "2.0",
            "id": "",
            "method": "query",
            "params": {
                "request_type": "call_function",
                "finality": "final",
                "account_id": self.validator_address,
                "method_name": "get_account_staked_balance",
                "args_base64": encoded_args
            }
        }
        resp = requests.post(self.view_base_url, json=params)
        r = resp.json()
        s = ''.join(chr(code) for code in r['result']['result'])
        s = s.strip('"')
        num = int(s)
        return num / 10 ** 24

    def get_account_unstaked_balance(self):
        s = '{"account_id": "'+self.address+'"}'
        b64_encoded = base64.b64encode(s.encode())
        encoded_args = b64_encoded.decode()
        params = {
            "jsonrpc": "2.0",
            "id": "",
            "method": "query",
            "params": {
                "request_type": "call_function",
                "finality": "final",
                "account_id": self.validator_address,
                "method_name": "get_account_unstaked_balance",
                "args_base64": encoded_args
            }
        }
        resp = requests.post(self.view_base_url, json=params)
        r = resp.json()
        s = ''.join(chr(code) for code in r['result']['result'])
        s = s.strip('"')
        num = int(s)
        return num / 10 ** 24

    def get_staking_pool_total_balance(self):
        s = '{"account_id": "' + self.address + '"}'
        b64_encoded = base64.b64encode(s.encode())
        encoded_args = b64_encoded.decode()
        params = {
            "jsonrpc": "2.0",
            "id": "",
            "method": "query",
            "params": {"request_type": "call_function",
                "finality": "final",
                "account_id": self.address,
                "method_name": "get_total_staked_balance",
                "args_base64": encoded_args}}
        resp = requests.post(self.view_base_url, json=params)
        r = resp.json()
        s = ''.join(chr(code) for code in r['result']['result'])
        s = s.strip('"')
        num = int(s)
        return num / 10 ** 24

    def get_validator_delegators_info(self):
        s = '{"account_id": "' + self.address + '", "from_index": 0, "limit": 100}'
        b64_encoded = base64.b64encode(s.encode())
        encoded_args = b64_encoded.decode()
        params = {
            "jsonrpc": "2.0",
            "id": "",
            "method": "query",
            "params": {
                "request_type": "call_function",
                "finality": "final",
                "account_id": self.address,
                "method_name": "get_accounts",
                "args_base64": encoded_args
            }
        }
        resp = requests.post(self.view_base_url, json=params)
        r = resp.json()
        s = ''.join(chr(code) for code in r['result']['result'])
        s = s.strip('"')
        delegators = json.loads(s)
        return delegators

    def _build_network_identifier(self):
        params = {'network_identifier': self._get_network_identifier()['network_identifiers'][0]}
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


def get_near_delegator_balance(address):
    n = NearNodesAnalytics(address)
    res = n.get_account_total_balance()
    pr = get_binance_current_priceCOSM('NEAR')
    res = {'available': res['available'], 'delegated': res['staked'], 'rewards': np.nan,
           'unbonding': res['unstaked'], 'total_balance': res['total'], 'price': pr}
    return res

def get_binance_current_priceCOSM(coin):
    r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT").json()
    return float(r['price'])