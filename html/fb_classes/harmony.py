import requests

class HarmonyNodesAnalytics():
    """
    Class for monitoring Harmony (ONE) assets
    """

    def __init__(self, address):
        self.address = address
        self.base_url = "https://api.s0.t.hmny.io"
        self.params = {"id": "1",
              "jsonrpc": "2.0"}

    def get_account_total_balance(self):
        available = self.get_available_balance()
        delegations = self.get_delegated_balance()
        total = available + delegations['delegated']+ delegations['rewards']
        res = {'total': total, 'available': available, 'staked': delegations['delegated'],
               'unstaked': delegations['undelegated'], 'rewards': delegations['rewards']}
        return res

    def get_available_balance(self):
        self.params["method"] = "hmyv2_getBalance"
        self.params["params"] = [self.address]
        response = requests.post(self.base_url, json=self.params)
        r = response.json()
        return r['result'] / 10 ** 18

    def get_delegated_balance(self):
        self.params["method"] = "hmy_getDelegationsByDelegator"
        self.params["params"] = [self.address]
        response = requests.post(self.base_url, json=self.params)
        r = response.json()
        und = 0
        dele = 0
        rew = 0
        for i in r['result']:
            for j in i['Undelegations']:
                und += j['Amount']
            dele += i['amount']
            rew += i['reward']
        return {'delegated': dele / 10 ** 18, 'undelegated': und / 10 ** 18, 'rewards': rew / 10 ** 18}

    def get_validator_info(self):
        self.params["method"] = "hmy_getValidatorInformation"
        self.params["params"] = [self.address]
        response = requests.post(self.base_url, json=self.params)
        r = response.json()
        return r


def get_harmony_delegator_balance(address):
    hh = HarmonyNodesAnalytics(address)
    res = hh.get_account_total_balance()
    pr = get_binance_current_priceCOSM('ONE')
    res = {'available': res['available'], 'delegated': res['staked'], 'rewards_to_claim': res['rewards'],
           'unbonding': res['unstaked'], 'total_balance': res['total'], 'price': pr}
    return res


def get_harmony_validator_balance(address):
    hh = HarmonyNodesAnalytics(address)
    res = hh.get_account_total_balance()
    pr = get_binance_current_priceCOSM('ONE')
    resu = {'available': res['available'], 'delegated': res['staked'], 'rewards_to_claim': res['rewards'],
            'unbonding': res['unstaked'], 'commissions_to_claim': 0,
            'total_balance': res['total'], 'price': pr}
    return resu


def get_harmony_validator_info_for_stakingRewards(address):
    api_url = "https://api.s0.t.hmny.io"
    params = {"id": "1",
              "jsonrpc": "2.0",
              "method": "hmy_getValidatorInformation",
              "params": [address]}
    response = requests.post(api_url, json=params)
    r = response.json()
    pr = get_binance_current_priceCOSM('ONE')
    bal= r['result']['total-delegation']/10**18
    num_delegators = len(r['result']['validator']['delegations'])

    res = {'tokenBalance': round(bal, 2),
         'balanceUsd': round(bal*pr, 2),
         'users': num_delegators,
         'fee': 0.1}
    return res

def get_binance_current_priceCOSM(coin):
    r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT").json()
    return float(r['price'])