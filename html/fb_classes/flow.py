import asyncio
from flow_py_sdk import cadence, flow_client, Script
import requests

def get_flow_delegator_balance(address, testnet=False):
    Address = cadence.Address
    addressFrom = Address.from_hex(address)
    tx_script = delegator_info_script(testnet)
    if testnet==True:
        host_name = {'name': 'access.devnet.nodes.onflow.org',
                     'port': 9000}
    elif testnet==False:
        host_name = {'name': 'access.mainnet.nodes.onflow.org',
                     'port': 9000}
    else:
        raise Exception('testnet must be True or False')

    script = Script(code=tx_script, arguments=[cadence.Address(addressFrom.bytes)])
    bal = asyncio.get_event_loop().run_until_complete(_get_flow_delegator_balance(script, addressFrom, host_name))
    pr = get_binance_current_priceCOSM('FLOW')
    locked = bal['tokensCommitted'] + bal['tokensUnstaking'] + bal['tokensUnstaked']
    total_bal = bal['available'] + locked + bal['tokensRewarded'] + bal['tokensStaked']
    res = {'available': bal['available'], 'delegated': bal['tokensStaked'], 'rewards': bal['tokensRewarded'],
           'unbonding': locked, 'total_balance': total_bal, 'price': pr}
    return res

async def _get_flow_delegator_balance(script, addressFrom, host_name):
    async with flow_client(host=host_name['name'], port=host_name['port']) as client:
        account = await client.get_account(address=addressFrom.bytes)
        available = account.balance / (10 ** 8)
    try:
        async with flow_client(host=host_name['name'], port=host_name['port']) as client:
            result = await client.execute_script(script=script)
        committed = result.fields['tokensCommitted'].value/ (10 ** 8)
        unstaking = result.fields['tokensUnstaking'].value/ (10 ** 8)
        unstaked = result.fields['tokensUnstaked'].value/ (10 ** 8)
        staked = result.fields['tokensStaked'].value/ (10 ** 8)
        rewards = result.fields['tokensRewarded'].value/ (10 ** 8)
    except:
        committed = 0
        unstaking = 0
        unstaked = 0
        staked = 0
        rewards = 0

    res = {'available': available,
           'tokensCommitted': committed,
           'tokensStaked': staked,
           'tokensUnstaking': unstaking,
           'tokensUnstaked': unstaked,
           'tokensRewarded': rewards}
    return res

IDENTITYTABLEADDRESS_TESTNET = ""
IDENTITYTABLEADDRESS_MAINNET = ""

def delegator_info_script(testnet):
    if testnet:
        IDENTITYTABLEADDRESS = IDENTITYTABLEADDRESS_TESTNET
    elif not testnet:
        IDENTITYTABLEADDRESS = IDENTITYTABLEADDRESS_MAINNET
    else:
        raise ValueError("testnet must be True or False")
    scr = '''
    import FlowIDTableStaking from ''' + IDENTITYTABLEADDRESS + '''

    // This script gets all the info about a delegator and returns it
    
    access(all) fun main(address: Address): FlowIDTableStaking.DelegatorInfo {
    
        let delegator = getAccount(address)
            .capabilities.borrow<&{FlowIDTableStaking.NodeDelegatorPublic}>(/public/flowStakingDelegator)
            ?? panic("Could not borrow reference to delegator object")
    
        return FlowIDTableStaking.DelegatorInfo(nodeID: delegator.nodeID, delegatorID: delegator.id)
    }
    '''
    return scr

def get_binance_current_priceCOSM(coin):
    r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT").json()
    return float(r['price'])

