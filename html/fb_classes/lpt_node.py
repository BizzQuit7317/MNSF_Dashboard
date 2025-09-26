from web3 import Web3
import lpt_info as chain_infos

class LptNodesAnalytics:
    def __init__(self, address='',
                 testnet=False):
        if testnet:
            lpt_token_contract = ''
            staking_contract = ''
            provider = ''
        else:
            lpt_token_contract = chain_infos.lpt_contract_address_mainnet
            staking_contract = chain_infos.lpt_staking_contract_address_mainnet
            provider = chain_infos.lpt_provider_mainnet
        token_abi = chain_infos.lpt_contract_abi
        staking_abi = chain_infos.lpt_staking_contract_abi

        self.w3 = Web3(Web3.HTTPProvider(provider))
        if len(address) > 0:
            self.address = self.w3.to_checksum_address(address)
        lpt_token_contract = self.w3.to_checksum_address(lpt_token_contract)
        staking_contract = self.w3.to_checksum_address(staking_contract)

        self.token_contract = self.w3.eth.contract(address=lpt_token_contract, abi=token_abi)
        self.staking_contract = self.w3.eth.contract(address=staking_contract, abi=staking_abi)

    def get_available_balance(self):
        return self.token_contract.functions.balanceOf(self.address).call()/1e18

    def get_delegator_info(self):
        r = self.staking_contract.functions.getDelegator(self.address).call()
        status = self.staking_contract.functions.delegatorStatus(self.address).call()
        pending_stake = self.staking_contract.functions.pendingStake(self.address, 0).call()/10**18
        res = {'bonded_amount': r[0]/1e18, 'fees': r[1]/1e18, 'delegate_address': r[2],
               'delegated_amount': r[3]/1e18, 'start_round': r[4], 'last_claim_round': r[5],
               'status': status, 'unbonding_lock_id': r[6], 'pending_stake': pending_stake}
        return res

    def get_unbonding_balance(self, unbond_id):
        r = self.staking_contract.functions.getDelegatorUnbondingLock(self.address, unbond_id).call()
        res = {'amount': r[0]/1e18, 'withdraw_round': r[1]}
        return res

    def get_eth_balance(self):
        return self.w3.eth.get_balance(self.address)/1e18

    def get_allowance(self, spender):
        return self.token_contract.functions.allowance(self.address, spender).call()/1e18


def get_lpt_delegator_balance(address, testnet=False):
    lpt = LptNodesAnalytics(address, testnet)
    available = lpt.get_available_balance()
    r = lpt.get_delegator_info()
    eth_bal = lpt.get_eth_balance()
    allowance = lpt.get_allowance(chain_infos.lpt_staking_contract_address_mainnet)
    res = {'available': available, 'delegated': r['bonded_amount'], 'unbonding': 0,
           'rewards_to_claim': 0, 'total_balance': available + r['pending_stake'],
           'eth_balance': eth_bal, 'allowance': allowance, 'commissions_to_claim': r['fees']}
    return res

