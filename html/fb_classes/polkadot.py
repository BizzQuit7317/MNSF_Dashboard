import numpy as np
from substrateinterface import SubstrateInterface
#from substrate-interface import substrate-interface as SubstrateInterface
try:
    from signal import signal, SIGPIPE, SIG_DFL

    signal(SIGPIPE,SIG_DFL)
except:
    pass

class PolkadotNodesAnalytics():
    def __init__(self, address, coin, testnet=False):
        self.address = address
        if (coin.lower() == 'kusama') or (coin.lower() == 'ksm'):
            self.ss_58 = 2
            self.coin_name = 'KSM'
            self.base_url = 'wss://kusama-rpc.polkadot.io'
            self.decimal = 12
        elif (coin.lower() == 'dot') or (coin.lower() == 'polkadot'):
            self.ss_58 = 0
            self.coin_name = 'DOT'
            self.base_url = 'wss://rpc.polkadot.io'
            self.decimal = 10
        else:
            raise Exception('Invalid coin name. Use dot or kusama.')
        if testnet:
            self.base_url = "wss://westend-rpc.polkadot.io"
            self.ss_58 = 42
            self.decimal = 12

        self.substrate = SubstrateInterface(
            url=self.base_url,
            ss58_format=self.ss_58,
            type_registry_preset='substrate-node-template')

    def get_total_balance(self):
        result = self.substrate.query(
            module='System',
            storage_function='Account',
            params=[self.address])
        data = result.decode()['data']
 
        #Once ksm id staking is unstaked comment this code out
        if self.address == '':
            data['free'] = data['reserved']

        total_balance = data['free']/10**self.decimal
        available = total_balance - data['frozen']/10**self.decimal

        result = self.substrate.query(
            module='Staking',
            storage_function='Ledger',
            params=[self.address])
        r = result.decode()
        if r:
            staked = r['active'] / 10 ** self.decimal
            unbonding = 0
            for i in r['unlocking']:
                unbonding += i['value'] / 10 ** self.decimal
        else:
            staked = 0
            unbonding = 0
        res = {'total_balance': total_balance, 'available': available,
               'staked': staked, 'unbonding': unbonding}
        return res

def get_polkadot_delegator_balance(address, coin, testnet=False):
    '''
    Get total balance of delegator
    '''
    p = PolkadotNodesAnalytics(address, coin, testnet)
    bal = p.get_total_balance()
    pr = get_binance_current_priceCOSM(p.coin_name)
    res = {'available': bal['available'], 'delegated': bal['staked'], 'rewards_to_claim': np.nan,
           'unbonding': bal['unbonding'], 'total_balance': bal['total_balance'], 'price': pr}
    return res

