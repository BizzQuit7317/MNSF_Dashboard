import requests, time
import pandas as pd
import numpy as np
## FUNCTION FOR PRICES
from urllib.parse import urlencode
from datetime import datetime
import hashlib, sys
import time, asyncio

sys.path.append("/var/www/html/fb_classes/")
import avax, cartesi, cosmos, flow, harmony, near, oasis, polkadot, tezos, eth_node, btc_node, lpt_node

sys.path.append("/var/www/html/html/")
import tmp

#print('Getting coin prices')

async def fetch_prices():
    symbols = ['BTC', 'XTZ', 'CTSI', 'ROSE', 'CREAM', 'NEAR', 'ETH', 'LPT',
               'ATOM', 'KAVA', 'SCRT', 'AVAX', 'ONE', 'KSM', 'FLOW']

    tasks = [asyncio.to_thread(avax.get_binance_current_priceCOSM, symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)
    return results

Prices = asyncio.run(fetch_prices())
price_time = datetime.now()
#print('Got coin prices')

#print('Attempting calls')

"""
try:
    custom_XTZ = customCoinsFB.XTZ
    custom_XTZ['USDValue'] = custom_XTZ['QTY'] * XTZPrice
    custom_XTZ['Price'] = XTZPrice
except:
    custom_XTZ = customCoinsFB.XTZ
"""
async def fetch_custom_coins(price_index, ID):
    XTZValue = 205000
    return {'Coin': 'XTZ', 'Contract': 'XTZ', 'QTY': XTZValue, 'USDValue': XTZValue * Prices[price_index], 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": ID, "Price": Prices[price_index]}

async def fetch_btc_node_price(address, price_index, ID):
    try:
        # Call the constructor and get the balance in a thread.
        btcNode = await asyncio.to_thread(btc_node.BtcNodeAnalytics, address)
        btcQTY = await asyncio.to_thread(btcNode.get_account_balance)
        btcPrice = btcQTY * Prices[price_index]
    except Exception as e:
        print(f"Error with calling Biance {ID}: {e}")
        btcQTY = 0
        btcPrice = 0
    return {'Coin': 'BTC', 'Contract': 'BTC', 'QTY': btcQTY, 'USDValue': btcPrice, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": ID, "Price": Prices[price_index]}

async def fetch_eth_balance(address, price_index, ID):
    try:
        result = await asyncio.to_thread(eth_node.EthNodesAnalytics, address)
        qty = float(result.get_delegated_balance())
        usd_value = qty * Prices[price_index]
    except Exception as e:
        print(f"Error with eth delegate: {e}")
        qty = 0
        usd_value = 0
    return {'Coin': 'ETH', 'Contract': 'ONE', 'QTY': qty, 'USDValue': usd_value, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": ID, "Price": Prices[price_index]}

async def fetch_eth_balance_m2(address, price_index, ID):
    try:
        result = await asyncio.to_thread(eth_node.EthNodesAnalytics, address)
        qty = float(result.get_available_balance())
        usd_value = qty * Prices[price_index]
    except Exception as e:
        print(f"Error with eth available: {e}")
        qty = 0
        usd_value = 0
    return {'Coin': 'ETH', 'Contract': 'ONE', 'QTY': qty, 'USDValue': usd_value, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": ID, "Price": Prices[price_index]}

async def fetch_polkadot_balance(address, price_index, id_str):
    # This function wraps the polkadot client calls
    try:
        client = await asyncio.to_thread(polkadot.PolkadotNodesAnalytics, address, 'ksm')
    except Exception as e:
        client = None

    ksmQTY = 0
    ksmPrice = 0
    if client:
        try:
            ksmQTY = await asyncio.to_thread(client.get_total_balance)
            # In case get_total_balance returns a dict:
            ksmQTY = ksmQTY.get('total_balance', 0) if isinstance(ksmQTY, dict) else ksmQTY
        except Exception as e:
            ksmQTY = 0
        try:
            ksmPrice = ksmQTY * Prices[price_index]
        except Exception as e:
            ksmPrice = 0
    return {'Coin': 'KSM', 'Contract': 'KSM', 'QTY': ksmQTY, 'USDValue': ksmPrice, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": id_str, "Price": Prices[price_index]}

async def fetch_cosmos_balance(address, price_index, coin, exchange, id_str):
    try:
        client = await asyncio.to_thread(cosmos.CosmosNodesAnalytics, address)
        balance = await asyncio.to_thread(client.get_total_balance)
        usd_value = balance * Prices[price_index]
    except Exception as e:
        balance = 0
        usd_value = 0
    return {'Coin': coin, 'Contract': coin, 'QTY': balance, 'USDValue': usd_value, 'Exchange': exchange, 'Account': 'SPOT', "ID": id_str, "Price": Prices[price_index]}

async def fetch_cosmos_kava_balance(address, price_index, coin, exchange, id_str):
    try:
        client = await asyncio.to_thread(cosmos.CosmosNodesAnalytics, address)
        balance = await asyncio.to_thread(client.get_total_balance_kava)
        usd_value = balance * Prices[price_index]
    except Exception as e:
        balance = 0
        usd_value = 0
    return {'Coin': coin, 'Contract': coin, 'QTY': balance, 'USDValue': usd_value, 'Exchange': exchange, 'Account': 'SPOT', "ID": id_str, "Price": Prices[price_index]}

async def fetch_cartesi_balance(address, contract, price_index, exchange, id_str):
    try:
        # In this case get the 'total_balance' from the returned dict.
        result = await asyncio.to_thread(cartesi.get_cartesi_delegator_balance, address, contract)
        balance = result.get('total_balance', 0)
        usd_value = float(balance) * Prices[price_index]
    except Exception as e:
        balance = 0
        usd_value = 0
    return {'Coin': 'CTSI', 'Contract': 'CARTESI', 'QTY': balance, 'USDValue': usd_value, 'Exchange': exchange, 'Account': 'SPOT', "ID": id_str, "Price": Prices[price_index]}

async def fetch_harmony_balance(address, price_index):
    try:
        result = await asyncio.to_thread(harmony.get_harmony_delegator_balance, address)
        qty = float(result.get('total_balance', 0))
        usd_value = qty * Prices[price_index]
    except Exception as e:
        qty = 0
        usd_value = 0
    return {'Coin': 'ONE', 'Contract': 'ONE', 'QTY': qty, 'USDValue': usd_value, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": "un", "Price": Prices[price_index]}

async def fetch_tezos_balance(address, price_index, exchange, id_str):
    try:
        result = await asyncio.to_thread(tezos.get_tezos_node_last_balance, address)
        qty = float(result)
        usd_value = qty * Prices[price_index]
    except Exception as e:
        qty = 0
        usd_value = 0
    return {'Coin': 'XTZ', 'Contract': 'TEZOS', 'QTY': qty, 'USDValue': usd_value, 'Exchange': exchange, 'Account': 'SPOT', "ID": id_str, "Price": Prices[price_index]}

async def fetch_avax_balance(avax_address, contract_address, price_index):
    try:
        result = await asyncio.to_thread(avax.get_avax_delegator_balance, avax_address, contract_address)
        qty = float(result.get('total_balance', 0))
        usd_value = qty * Prices[price_index]
    except Exception as e:
        qty = 0
        usd_value = 0
    return {'Coin': 'AVAX', 'Contract': 'AVAX', 'QTY': qty, 'USDValue': usd_value, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": "staking", "Price": Prices[price_index]}

async def fetch_near_balance(api_key, price_index):
    try:
        client = await asyncio.to_thread(near.NearNodesAnalytics, api_key)
        result = await asyncio.to_thread(client.get_account_total_balance)
        qty = result.get('total', 0)
        usd_value = float(qty) * Prices[price_index]
    except Exception as e:
        qty = 0
        usd_value = 0
    return {'Coin': 'NEAR', 'Contract': 'NEAR', 'QTY': qty, 'USDValue': usd_value, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": "staking", "Price": Prices[price_index]}

async def fetch_flow_balance(address, price_index):
    try:
        result = await asyncio.to_thread(flow.get_flow_delegator_balance, address, False)
        qty = float(result.get('total_balance', 0))
        usd_value = qty * Prices[price_index]
    except Exception as e:
        qty = 0
        usd_value = 0
    return {'Coin': 'FLOW', 'Contract': 'FLOW', 'QTY': qty, 'USDValue': usd_value, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": "un", "Price": Prices[price_index]}

async def fetch_lpt_balance(address, price_index, exchange, id_str):
    try:
        result = await asyncio.to_thread(lpt_node.get_lpt_delegator_balance, address)
        qty = result.get('total_balance', 0)
        usd_value = qty * Prices[price_index]
    except Exception as e:
        qty = 0
        usd_value = 0
    return {'Coin': 'LPT', 'Contract': 'LPT', 'QTY': qty, 'USDValue': usd_value, 'Exchange': exchange, 'Account': 'SPOT', "ID": id_str, "Price": Prices[price_index]}

async def fetch_oasis_balance(address, price_index):
    try:
        balance = await asyncio.to_thread(oasis.get_oasis_wallet_total_balance, address)
        usd_value = float(balance) * Prices[price_index]
        coin_name = 'ROSE'
    except Exception as e:
        balance = 0
        usd_value = 0
        coin_name = 'ROSE Old'
    return {'Coin': coin_name, 'Contract': 'ROSE', 'QTY': balance, 'USDValue': usd_value, 'Exchange': 'FireBlocks', 'Account': 'SPOT', "ID": "un", "Price": Prices[price_index]}

# You would add similar async helper functions for the remaining sections (e.g., additional KSM staked balances,
# ETH balances, additional Tezos calls, Cosmos staked/cold balances, etc.) following the same pattern.

async def main():
    print("starting")
    tasks = []

    # Example tasks for BTC (two addresses):
    tasks.append(fetch_btc_node_price("", 0, "staking"))
    tasks.append(fetch_btc_node_price("", 0, "staking_2"))
    print("btc tasks apended")    

    # Polkadot / KSM tasks (the second argument '13' refers to Prices[13] for KSM)
    tasks.append(fetch_polkadot_balance('', 13, "staking"))
    tasks.append(fetch_polkadot_balance('', 13, "staking_3"))
    tasks.append(fetch_polkadot_balance('', 13, "staking_5"))
    tasks.append(fetch_polkadot_balance('', 13, "staking_2"))
    tasks.append(fetch_polkadot_balance('', 13, "staking"))
    tasks.append(fetch_polkadot_balance('', 13, "staking_2"))
    print("polkadot tasks appended") 

    # Cosmos example for ATOM – Prices[8]:
    tasks.append(fetch_cosmos_balance('', 8, 'ATOM', 'FireBlocks', "staking"))
    # Cosmos Cold ATOM (if needed):
    tasks.append(fetch_cosmos_balance('', 8, 'ATOM', 'FireBlocks_Cold', "cold"))
    print("cosmos tasks appended")

    #SCRT
    tasks.append(fetch_cosmos_balance('', 10, 'SCRT', 'FireBlocks', "staking"))
    print("scrt tasks appeneded")

    #KAVA
    tasks.append(fetch_cosmos_kava_balance('', 9, 'KAVA', 'FireBlocks', "staking"))    
    print("kava tasks appended")

    # Cartesi CTSI example – Prices[2]:
    tasks.append(fetch_cartesi_balance('', "", 2, 'FireBlocks', "staking"))
    tasks.append(fetch_cartesi_balance('', "", 2, 'FireBlocks_Cold', "cold"))
    print("ctsi tasks appended")    

    # Harmony ONE – Prices[12]:
    tasks.append(fetch_harmony_balance('', 12))
    print("Harmony tasks appended")
    # Tezos examples – Prices[1]:
    tasks.append(fetch_tezos_balance('', 1, 'FireBlocks', "staking"))
    tasks.append(fetch_tezos_balance('', 1, 'FireBlocks_Cold', "cold"))
    print("Tezos tasks appended")
    # AVAX – Prices[11]:
    tasks.append(fetch_avax_balance('', '', 11))
    print("AVAX tasks appended")
    
    """
    # NEAR – Prices[5]:
    tasks.append(fetch_near_balance('', 5))
    print("NEAR tasks appended")
    """

    # FLOW – Prices[14]:
    tasks.append(fetch_flow_balance('', 14))
    print("FLOW tasks appended")
    # LPT examples – Prices[7]:
    tasks.append(fetch_lpt_balance("", 7, 'FireBlocks', "staking"))
    tasks.append(fetch_lpt_balance("", 7, 'FireBlocks_Cold', "cold"))
    print("LPT tasks appended")
    # Oasis ROSE – Prices[3]:
    tasks.append(fetch_oasis_balance('', 3))
    print("Oasis tasks appended")
    # (You can add additional tasks here for ETH, additional Tezos calls, etc. following the same pattern.)
    tasks.append(fetch_eth_balance("", 6, "staking"))
    tasks.append(fetch_eth_balance_m2("", 6, "available"))
    print("ETH tasks appended")
    tasks.append(fetch_custom_coins(1, "staking_2"))    
    print("Tezos tasks appended")
    # Run all tasks concurrently:
    print("starting tasks up")
    results = await asyncio.gather(*tasks)
    print("tasks run\nformatting data") 
    df = pd.DataFrame(results)
    new_usdvalue = df['USDValue'].sum()
    #print(f"New FireBlocks Method\nUSDValue Sum: {df['USDValue'].sum():,.2f}")
    #df['QTY'] = df['QTY'].apply(lambda x: f"{x:,}".rstrip('0').rstrip('.') if x != 0 else "0")
    df['u1'] = df['USDValue'].astype(float)
    #df['USDValue'] = df['USDValue'].apply(lambda x: f"{x:,}".rstrip('0').rstrip('.') if x != 0 else "0")
    df['p1'] = df['Price'].astype(float)
    #df['Price'] = df['Price'].apply(lambda x: f"{x:,}".rstrip('0').rstrip('.') if x != 0 else "0")
    df = df.sort_values(by=["Coin", "Exchange"])
    df.drop(["u1", "p1"], axis=1, inplace=True)

    df['price_time'] = str(price_time)

    breakdown = {'Exchange':'FireBlocks', 'USDT-M':0, 'SPOT':new_usdvalue, 'Margin':0, 'Earn':0, 'Coin-M':0, 'Total':new_usdvalue}
    values = df.to_dict(orient='records')

    with open ('data/fireBlocks.py', 'w') as f:
        f.write(f"values = {str(values)}")
        f.write('\n')
        f.write(f"breakdown = {str(breakdown)}")##
    print('Finsished')
    time.sleep(1800)
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 10000):
    #    print(df)

    #print("\n")

    """
    df2 = pd.DataFrame(tmp.breakdown_constructor_raw)
    df2 = df2[(df2['Exchange'] == "FireBlocks") | (df2['Exchange'] == "FireBlocks_Cold")]
    df2 = df2[df2["Coin"] != "USDC"]
    old_usdvalue = df2['USDValue'].sum()
    #print(f"Current FireBlocks Method\nUSDValue Sum: {df2['USDValue'].sum():,.2f}")
    df2['QTY'] = df2['QTY'].apply(lambda x: f"{x:,}".rstrip('0').rstrip('.') if x != 0 else "0")
    df2['u2'] = df2['USDValue'].astype(float)
    df2['USDValue'] = df2['USDValue'].apply(lambda x: f"{x:,}".rstrip('0').rstrip('.') if x != 0 else "0")
    df2['p2'] = df2['Price'].astype(float)
    df2['Price'] = df2['Price'].apply(lambda x: f"{x:,}".rstrip('0').rstrip('.') if x != 0 else "0")
    df2 = df2.sort_values(by=["Coin", "Exchange"])
    df2.drop(["Contract", "Account"], axis=1, inplace=True)
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 10000):
    #    print(df2)

    print("\n")
    

    df3 = pd.concat([df.reset_index(drop=True), df2.reset_index(drop=True)], axis=1)
    df3.insert(loc=8, column="     ", value="     ")
    df3['Price Diff'] = df3['p1'] - df3['p2']
    df3['USD Diff'] = df3['u1'] - df3['u2']
    df3['Price Diff'] = df3['Price Diff'].apply(lambda x: f"{x:,}".rstrip('0').rstrip('.') if x != 0 else "0")
    df3['USD Diff'] = df3['USD Diff'].apply(lambda x: f"{x:,}".rstrip('0').rstrip('.') if x != 0 else "0")
    df3.insert(loc=18, column="    ", value="    ")
    df3.drop(['p1', 'p2', 'u1', 'u2'], axis=1, inplace=True)
    print(f"New FireBlocks Method                                                                                                              Current FireBlocks Method\nUSDValue Sum: {new_usdvalue:,.2f}                                                                                                         USDValue Sum: {old_usdvalue:,.2f} \n")
    #df3['Price Diff'] = 0
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 10000):
        print(df3)
 
    print(f"\nUSDValue Difference: {(new_usdvalue-old_usdvalue):,.2f}")
    """
    

asyncio.run(main())
