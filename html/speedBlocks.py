import pandas as pd
import numpy as np
import sys, asyncio, requests
from datetime import date
from aiohttp import ClientSession
sys.path.append('/var/www/html/Exchange_Functions/')
sys.path.append('/var/www/html/config/')
sys.path.append('/var/www/html/data/')
sys.path.append('/var/www/html/html/')
import fireBlocks
import customCoins
import Binance as b
import Bybit as by
import keys as k
import HR as h
import tmp
import Gate as g
import Kraken as kr
import Okx as ok
import falconx as fal
import datetime

GAV_VALUE = customCoins.GAV

BTC_price_b = b.get_binance_current_price("BTC", "USDT")
ETH_price_b = b.get_binance_current_price("ETH", "USDT")

todays_date = date.today()
DAY = int(todays_date.day) - 1

async def fetch(session, coin):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
    async with session.get(url) as response:
        return await response.json()

async def getUSD(row, session):
    try:
        r = await fetch(session, row['Coin'])
        return float(r['price']) * float(row['QTY'])
    except Exception as e:
        print(f"ERROR IN GETTING USDVALUE IN SPEEDBLOCKS LINE 27\nError: {e}")
        return 1

async def get_balance(apiKey, apiSec):
    try:
        bin_total = b.totalBinance(apiKey, apiSec, "Binance")
        return bin_total['USDValue'].sum()
    except Exception as e:
        print(f"Error in binance: {e}")
        return 1

    #url = f"https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    #x = b.binance_send_signed_request("https://api.binance.com", 'GET', '/sapi/v1/asset/wallet/balance', apiKey, apiSec, payload={})
    #df_balance = pd.DataFrame(x)
    #df_balance['balance'] = df_balance['balance'].astype(float)
    #dfSum = df_balance['balance'].sum()
    #dfSum = dfSum * float(requests.get(url).json()['price'])
    #return float(dfSum)

async def main():
    async with ClientSession() as session:
        """
        tasks = [getUSD(row, session) for _, row in df.iterrows()]
        usd_values = await asyncio.gather(*tasks)
        df['USD'] = usd_values
        dat = df['USD'].sum()
        """
        dat = df['USDValue'].sum()
        tot = f"tot = {dat}"

        dfSum = await get_balance(k.binance_key, k.binance_secret)
        dfSum += await get_balance(k.binance_sub1_key, k.binance_sub1_secret)
        dfSum += await get_balance(k.binance_sub2_key, k.binance_sub2_secret)
        dfSum += await get_balance(k.binance_sub3_key, k.binance_sub3_secret)
        #dfSum += await get_balance(k.binance_hr_key, k.binance_hr_secret)
        dfSum += await get_balance(k.binance_sub4_key, k.binance_sub4_secret)
        binance = f"bin = {dfSum}"

        byb = by.get_v5_balance(k.bybit_key, k.bybit_secret)
        bybits = byb['result']['list'][0]['totalEquity']

        #bybs = by.get_v5_balance(k.bybit_hr_key, k.bybit_hr_secret)
        bybitss = 0#bybs['result']['list'][0]['totalEquity']

        bybs1 = by.get_v5_balance(k.bybit_sub_1_key, k.bybit_sub_1_secret)
        bybatss1 = bybs1['result']['list'][0]['totalEquity']

        bybiter = float(bybits) + float(bybitss) + float(bybatss1)

        bybitFund = by.get_v5_fund(k.bybit_key, k.bybit_secret)
        bybitFundStripped = bybitFund['result']['balance']
        for i in bybitFundStripped:
            bybiter += float(i['walletBalance'])

        #bybitFund = by.get_v5_fund(k.bybit_hr_key, k.bybit_hr_secret)
        #bybitFundStripped = #bybitFund['result']['balance']
        #for i in bybitFundStripped:
        #    bybiter += float(i['walletBalance'])

        bybitFund = by.get_v5_fund(k.bybit_sub_1_key, k.bybit_sub_1_secret)
        bybitFundStripped = bybitFund['result']['balance']
        for i in bybitFundStripped:
            bybiter += float(i['walletBalance'])

        #bybiter = float(bybits) + float(bybitss)
        bybit = f"by = {bybiter}"
        
        try:
            okx_loans = ok.get_loans(k.okx_key, k.okx_secret, k.okx_passphrase)['USDValue'].sum()
        except:
            okx_loans = 0
        okx_total = float(ok.speed_balance(k.okx_key, k.okx_secret, k.okx_passphrase)) #+ ok.get_loans(k.okx_key, k.okx_secret, k.okx_passphrase)['USDValue'].sum()
  
        try:
            falconx = fal.Client(k.falconx_key, k.falconx_secret, k.falconx_pass).get_assets("Falconx")
            falconx_total = falconx['USDValue'].astype(float).sum()
        except :
            falconx_total = 0
        try:
            falconx_total += customCoins.TAO['USDValue']
        except:
            print("DIDNT ADD CUSTOM TAO!!!!!!!!!!!!!!!!!!")
            pass
        try:
            okx_total += float(okx_loans)
            if okx_total < 0:
                okx_total = 0
        except Exception as e:
            print(f"Error adding okx_loan: {e}")

        url = f"https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
        url2 = f"https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        btc_price = requests.get(url2).json()['price']
        eth_price = requests.get(url).json()['price']
        df_tmp = pd.DataFrame([{"Coin":"BTC", "Price":btc_price, "Time":datetime.datetime.now()}, {"Coin":"ETH", "Price":eth_price, "Time":datetime.datetime.now()}])
        df_tmp.to_csv("eth_btc_price.csv")
        try:
            banks = (float(customCoins.ETH['QTY']) * float(eth_price)) + float(customCoins.USD['QTY']) + (float(customCoins.BTC['QTY']) * float(btc_price))
        except Exception as e:
            print(f'went wrong eth: {e}')
            banks = 0
        #HR = h.walletBalance(k.hr_key, k.hr_secret)
        #HR = HR['QTY'].sum()
        #HRR = f"hr = {HR}"

        try:
            gatePrice = g.gate_total_balance(k.gate_key, k.gate_secret, 'Gate')
            #print(gatePrice)
            gatePrice = float(gatePrice['USDValue'].sum())
        except:
            gatePrice = 0

        try:
            gateSubPrice = g.gate_total_balance(k.gate_sub_key, k.gate_sub_secret, 'Gate')
            #print(gateSubPrice)
            gateSubPrice = float(gateSubPrice['USDValue'].sum())
        except:
            gateSubPrice = 0


        #print(gatePrice, gateSubPrice)

        krak = kr.kraken_spot_wallet_balance(k.kraken_key, k.kraken_secret, 'Kraken')
        krak = krak['USDValue'].sum()
 
        #overalll = falconx_total + gateSubPrice + float(bybiter) + float(dfSum) + float(dat) + float(customCoins.Credinvest['QTY']) + float(banks) + float(HR) + gatePrice + float(krak) + float(okx_total) + float(customCoins.invoice['QTY'])
        """
        overalll = falconx_total + gateSubPrice + float(bybiter) + float(dfSum) + float(dat) + float(customCoins.Credinvest['QTY']) + float(banks) + gatePrice + float(krak) + float(okx_total) + float(customCoins.invoice['QTY'])        
        This has OKX need to return to this when okx is working properly
        """

        try:
            customLP = float(customCoins.LP['QTY']) * float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=LPTUSDT").json()['price'])
        except Exception as e:
            print(f"Error adding cunting lpt: {e}")
            customLP = 0

        overalll = falconx_total + gateSubPrice + float(bybiter) + float(dfSum) + float(dat) + float(customCoins.Credinvest['QTY']) + float(banks) + gatePrice + float(krak) + float(customCoins.invoice['QTY']) + customLP + float(customCoins.option['QTY']) + float(customCoins.note['QTY'])

        #overalll = falconx_total + gateSubPrice + float(bybiter) + float(dfSum) + float(dat) + float(customCoins.Credinvest['QTY']) + float(banks) + gatePrice + float(krak) + float(customCoins.invoice['QTY']) + float(customCoins.LP['QTY'])

        #print(f"Overall should be 8,611,751\n{overalll}\n{dat}\n{customCoins.Credinvest['QTY']}\n{customCoins.USDT['QTY']}\n{banks}")

        overall = f"over = {overalll}"

        formatted = tmp.balance
        staked = formatted[0]['Staked Value']
        staked = float(staked.replace(',', ''))
        avg = formatted[0]['Ave Staked Dur']

        ##calc = staked / overalll

        delta = tmp.aggAssets
        delta = pd.DataFrame(delta)
        delta['USDValue'] = delta['USDValue'].str.replace(',', '').astype(float)
        delta = delta['USDValue'].sum()
        if np.isinf(delta):
            delta = 0
        if delta > 999999999999:
            delta = 0

        gav = ((float(overalll) - GAV_VALUE) / GAV_VALUE) * 100

        bpnl = customCoins.BTC_gav * (BTC_price_b - customCoins.BTCpx_gav)
        epnl = customCoins.ETH_gav * (ETH_price_b - customCoins.ETHpx_gav)

        prc = customCoins.monthly_cost / 30 * DAY

        mf = customCoins.NAV * 0.02 / 365 * DAY
	
        pf = overalll - GAV_VALUE - prc - mf
        if pf < 0:
                pf = 0
        else:
                pf *= 0.2

        #pf = 0.2 * (overalll - GAV_VALUE - prc - mf)

        n = customCoins.NAV + bpnl + epnl + (overalll - GAV_VALUE) - prc - mf - pf

        calc = staked / n

        gm = overalll - GAV_VALUE
        nm = ((gm - prc - mf - pf) / customCoins.NAV) * 100

        gavPercent = ((overalll - GAV_VALUE) / GAV_VALUE) * 100
        with open("/home/ubuntu/total_py_written.log", 'a') as f:
           f.write(f"total.py written to at {datetime.datetime.now()}\n##############################################################\n")
        with open('/var/www/html/html/total.py', 'w') as f:
            try:
                f.write(f"falconx = {falconx_total}")
            except:
                f.write("falconx = 0")
            f.write('\n')
            try:
                f.write(f"gate_sub = {gateSubPrice}")
            except:
                f.write("gate_sub = 0")
            f.write('\n')
            try:
                f.write(f"gate = {gatePrice}")
            except:
                f.write("gate = 0")
            f.write('\n')
            try:
                f.write(f"kraken = {krak}")
            except:
                f.write("kraken = 0")
            f.write('\n')
            try:
                f.write(f"Invoice = {customCoins.invoice['QTY']}")
            except:
                f.write("Invoice = 0")
            f.write('\n')
            try:
                f.write(tot)
            except:
                f.write(f"tot = 0")
            f.write('\n')
            try:
                f.write(binance)
            except:
                f.write(f"bin = 0")
            f.write('\n')
            try:
                f.write(bybit)
            except:
                f.write(f"by = 0")
            f.write('\n')
            try:
                f.write(overall)
            except:
                f.write(f"over = 0")
            f.write('\n')
            try:
                f.write(f"cred = {customCoins.Credinvest['QTY']}")
            except:
                f.write(f"cred = 0")
            f.write('\n')
            try:
                f.write(f"herc = {customCoins.USDT['QTY']}")
            except:
                f.write(f"herc = 0")
            f.write('\n')
            try:
                f.write(f"banks = {banks}")
            except:
                f.write(f"banks = 0")
            f.write('\n')
            try:
                f.write(HRR)
            except:
                f.write(f"hr = 0")
            f.write('\n')
            try:
                f.write(f"stake = {staked}")
            except:
                f.write(f"stake = 0")
            f.write('\n')
            try:
                f.write(f"avg = {avg}")
            except:
                f.write(f"avg = 0")
            f.write('\n')
            try:
                f.write(f"calc = {calc}")
            except:
                f.write(f"calc = 0")
            f.write('\n')
            try:
                f.write(f"delta = {delta}")
            except:
                f.write(f"delta = 0")
            f.write('\n')
            try:
                f.write(f"gav = {gav}")
            except:
                f.write(f"gav = 0")
            f.write('\n')
            try:
                f.write(f"gavValue = {GAV_VALUE}")
            except:
                f.write(f"gavValue = (0)")
            f.write('\n')
            try:
                f.write(f"NAV = {customCoins.NAV}")
            except:
                f.write(f"NAV = 0")
            f.write('\n')
            try:
                f.write(f"BTC_gav = {customCoins.BTC_gav}")
            except:
                f.write(f"BTC_gav = 0")
            f.write('\n')
            try:
                f.write(f"ETH_gav = {customCoins.ETH_gav}")
            except:
                f.write(f"ETH_gav = 0")
            f.write('\n')
            try:
                f.write(f"BTCpx_gav = {customCoins.BTCpx_gav}")
            except:
                f.write(f"BTCpx_gav = 0")
            f.write('\n')
            try:
                f.write(f"ETHpx_gav = {customCoins.ETHpx_gav}")
            except:
                f.write(f"ETHpx_gav = 0")
            f.write('\n')
            try:
                f.write(f"monthly_cost = {customCoins.monthly_cost}")
            except:
                f.write(f"monthly_cost = 0")
            f.write('\n')
            try:
                f.write(f"BTC_price_b = {BTC_price_b}")
            except Exception as e:
                #print(f"{e}")
                f.write(f"BTC_price_b = 0")
            f.write('\n')
            try:
                f.write(f"ETH_price_b  = {ETH_price_b}")
            except:
                f.write(f"ETH_price_b = 0")
            f.write('\n')
            try:
                f.write(f"bpnl  = {bpnl}")
            except:
                f.write(f"bpnl = 0")
            f.write('\n')
            try:
                f.write(f"epnl  = {epnl}")
            except:
                f.write(f"epnl = 0")
            f.write('\n')
            try:
                f.write(f"prc  = {prc}")
            except:
                f.write(f"prc = 0")
            f.write('\n')
            try:
                f.write(f"mf  = {mf}")
            except:
                f.write(f"mf = 0")
            f.write('\n')
            try:
                f.write(f"pf  = {pf}")
            except:
                f.write(f"pf = 0")
            f.write('\n')
            try:
                f.write(f"n  = {n}")
            except:
                f.write(f"n = 0")
            f.write('\n')
            try:
                f.write(f"gm  = {gm}")
            except:
                f.write(f"gm = 0")
            f.write('\n')
            try:
                f.write(f"nm  = {nm}")
            except:
                f.write(f"nm = 0")
            f.write('\n')
            try:
                f.write(f"gavPercent  = {gavPercent}")
            except:
                f.write(f"gavPercent = 0")
            print('completed')

df = pd.DataFrame(fireBlocks.values)
df['Timer'] = datetime.datetime.now()
df.to_csv("/var/www/html/speedBlocks_fb.csv")
asyncio.run(main())
