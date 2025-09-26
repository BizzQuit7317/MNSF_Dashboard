import sys, time, requests, pytz, traceback
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None
from datetime import datetime, timezone, timedelta

start = time.time()

print("Started!")

[sys.path.append(directory) for directory in ['Exchange_Functions', 'config', 'data', 'html']]
import Binance
print("Binance") 
import Bybit
print("Bybit")
import Huobi
print("Huobi")
import Kraken
print("Kraken")
import Okx
print("Okx")
import keys
print("keys")
import customCoins
print("customCoins")
import fireBlocks
print("fireBlocks")
import customPos
print("customPos")
import CustomUSDC
print("CustomUSDC")
import fundStore
print("fundStore")
import HR
print("HR")
import Gate
print("Gate")
import report
print("report")
import falconx
print("falconx")

print("Imports done")

######Additional calls
#fundingData = pd.DataFrame(requests.get('http://18.130.218.34:8080/').json()['message'])
#fundFull = 'funding = '+str(fundingData.to_dict(orient='records'))
#df = pd.DataFrame(fundingData)
#unique_exchanges = df['Exchange'].unique()
#dfs = []
#for i in unique_exchanges:
#    dfx = df[df['Exchange'] == i]
#    dfx.rename(columns={'Funding': i}, inplace=True)
#    dfx = dfx[['Symbol', i]]
#    dfx[i] = dfx[i].apply(lambda x: f'{x:,.6f}')
#    dfs.append(dfx)
#df = pd.concat(dfs, axis=0)
#df = df.groupby(['Symbol']).agg({
#            'Huobi':'last',
#            'Binance':'last',
#            'Bybit':'last',
#            'OKX':'last',
#            'Gate':'last'
#        }).reset_index()
#df = df.fillna(0)
#with open('html/fundStore.py', 'w') as f:
#    fund = 'fundingFormat = '+str(df.to_dict(orient='records'))
#    f.write(fund)
#    f.write('\n')
#    f.write(fundFull)
fundingData = requests.get('http://18.130.218.34:8080/').json()['message']
funding = f"funding = {str(fundingData)}"
fundFull = f"fundingFormat = {str(fundingData)}"

with open('html/fundStore.py', 'w') as f:
    f.write(funding)
    f.write('\n')
    f.write(fundFull)

######Calling customCoins
variables = [attr for attr in dir(customCoins) if not callable(getattr(customCoins, attr)) and not attr.startswith("__")]
variable_values = []
for variable_name in variables:
    variable_value = getattr(customCoins, variable_name)
    variable_values.append(variable_value)

print("Just before calling exchanges")

######Calling all general data
try:
    falconxData = falconx.Client(keys.falconx_key, keys.falconx_secret, keys.falconx_pass).get_assets("Falconx")
except:
    #falconxData = pd.DataFrame(pd.DataFrame([{"Coin":"TAO", "Contract":"TAO","QTY":6084.26, "USDValue":(6084.26 * float(requests.get('https://api.binance.com/api/v3/ticker/price?symbol=TAOUSDT').json()['price'])), "Exchange":"Falconx", "Account":"SPOT", "ID":"Staking"}]))
    falconxData = pd.DataFrame()

binanceData = Binance.totalBinance(keys.binance_key, keys.binance_secret, 'Binance')
bybitData = Bybit.total_bybit_balance(keys.bybit_key, keys.bybit_secret, 'Bybit')
huobiData = Huobi.total_huobi_balance(keys.huobi_key, keys.huobi_secret, keys.huobi_spot_id, 'Huobi')
krakenData = Kraken.kraken_spot_wallet_balance(keys.kraken_key, keys.kraken_secret, 'Kraken')
okxData = Okx.okx_wallet_total(keys.okx_key, keys.okx_secret, keys.okx_passphrase, 'Okx')
#binanceHRData = Binance.totalBinance(keys.binance_hr_key, keys.binance_hr_secret, 'Binance_HR')
#bybitHRData = Bybit.total_bybit_balance(keys.bybit_hr_key, keys.bybit_hr_secret, 'Bybit_HR')
#okxHRData = Okx.okx_wallet_total(keys.okx_hr_key, keys.okx_hr_secret, keys.okx_hr_passphrase, 'Okx_HR')
binanceSub1Data = Binance.totalBinance(keys.binance_sub1_key, keys.binance_sub1_secret, 'Binance_Sub1')
binanceSub2Data = Binance.totalBinance(keys.binance_sub2_key, keys.binance_sub2_secret, 'Binance_Sub2')
fireBlocksData = fireBlocks.values
try:
    USDC = CustomUSDC.get_usdc_wallet_total_balance(keys.customUSDC)
except:
    USDC = pd.DataFrame()
binanceSub3Data = Binance.totalBinance(keys.binance_sub3_key, keys.binance_sub3_secret, 'Binance_Sub3')
#HRData = HR.walletBalance(keys.hr_key, keys.hr_secret)
GateData = Gate.gate_total_balance(keys.gate_key, keys.gate_secret, 'Gate')
binanceSub4Data = Binance.totalBinance(keys.binance_sub4_key, keys.binance_sub4_secret, 'Binance_Sub4')
bybitSub1Data = Bybit.total_bybit_balance(keys.bybit_sub_1_key, keys.bybit_sub_1_secret, 'Bybit_Sub1')
gateSub1 = Gate.gate_total_balance(keys.gate_sub_key, keys.gate_sub_secret, 'Gate_Sub1')
##okxDataLoan = Okx.get_loans(keys.okx_key, keys.okx_secret, keys.okx_passphrase)


######Calling OKX Loan data
##try:
##    okx_loan_data = Okx.get_loan_info(keys.okx_key, keys.okx_secret, keys.okx_passphrase)
##except:
##    okx_loan_data = {"Loan Amount":0, "Collateral":0, "Current LTV":0, "Margin Call LTV":0, "Liquidation LTV":0, "Liquidation Price":0}

#okx_loan_data = Okx.get_loan_info(keys.okx_key, keys.okx_secret, keys.okx_passphrase)

##print(f"OKX LOAN VALUE: {okx_loan_data}")

######Calling all position data
binancePos = Binance.all_positions(keys.binance_key, keys.binance_secret, 'Binance')
bybitPos = Bybit.get_usdt_pos(keys.bybit_key, keys.bybit_secret, 'Bybit')
huobiPos = Huobi.get_all_positions(keys.huobi_key, keys.huobi_secret, 'Huobi')
okxPos = Okx.get_usdt_pos(keys.okx_key, keys.okx_secret, keys.okx_passphrase, 'Okx')
#binanceHRPos = Binance.all_positions(keys.binance_hr_key, keys.binance_hr_secret, 'Binance_HR')
#bybitHRPos = Bybit.get_usdt_pos(keys.bybit_hr_key, keys.bybit_hr_secret, 'Bybit_HR')
#okxHRPos = Okx.get_usdt_pos(keys.okx_hr_key, keys.okx_hr_secret, keys.okx_hr_passphrase, 'Okx_HR')
binanceSub1Pos = Binance.all_positions(keys.binance_sub1_key, keys.binance_sub1_secret, 'Binance_Sub1')
binanceSub2Pos = Binance.all_positions(keys.binance_sub2_key, keys.binance_sub2_secret, 'Binance_Sub2')
customPos = customPos.get()
binanceSub3Pos = Binance.all_positions(keys.binance_sub3_key, keys.binance_sub3_secret, 'Binance_Sub3')
GatePos = Gate.get_usdt_pos(keys.gate_key, keys.gate_secret, 'Gate')
binanceSub4Pos = Binance.all_positions(keys.binance_sub4_key, keys.binance_sub4_secret, 'Binance_Sub4')
bybitSub1Pos = Bybit.get_usdt_pos(keys.bybit_sub_1_key, keys.bybit_sub_1_secret, 'Bybit_Sub1')
gateSub1Pos = Gate.get_usdt_pos(keys.gate_sub_key, keys.gate_sub_secret, 'Gate_Sub1')

def allPositions():
    df = pd.concat([gateSub1Pos, bybitSub1Pos, binanceSub4Pos, GatePos, binanceSub3Pos, customPos, binancePos, bybitPos, huobiPos, okxPos, binanceSub1Pos, binanceSub2Pos], ignore_index=True)
    df = df.fillna(0)
    return df

def allBalance():
    #falconx_staking = falconxData[falconxData['id'] == 'staking']
    ##df = pd.concat([okxDataLoan, falconxData, gateSub1, bybitSub1Data, binanceSub4Data, GateData, binanceSub3Data, binanceData, bybitData, huobiData, krakenData, okxData, binanceSub1Data, binanceSub2Data, USDC], ignore_index=True)
    df = pd.concat([falconxData, gateSub1, bybitSub1Data, binanceSub4Data, GateData, binanceSub3Data, binanceData, bybitData, huobiData, krakenData, okxData, binanceSub1Data, binanceSub2Data, USDC], ignore_index=True)
    variables = [attr for attr in dir(customCoins) if not callable(getattr(customCoins, attr)) and not attr.startswith("__")]
    variable_values = []
    for variable_name in variables:
        variable_value = getattr(customCoins, variable_name)
        try:
            variable_value['USDValue'] = variable_value['QTY'] * float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={variable_value['Coin']}USDT").json()['price'])
            variable_values.append(variable_value)
        except:
            try:
                variable_value['USDValue'] = variable_value['QTY']
                variable_values.append(variable_value)
            except:
                pass
    df2 = pd.DataFrame(variable_values)
    #print(df2)
    df3 = pd.DataFrame(fireBlocksData)

    df = pd.concat([df, df2, df3], axis=0)
    return df

def BalPos(dfB, dfP):
    df = pd.concat([dfB, dfP], ignore_index=True)
    return df

def totalBalance(df):
    df['USDValue'] = df['USDValue'].astype(float)
    return df['USDValue'].sum()

def remove_coins(df, coins_to_exclude):
    return df[~df['Coin'].isin(coins_to_exclude)]
    #coins_to_exclude = ['USD', 'USDT', 'USDC', 'EUR', 'BUSD', 'ZUSD']

def keep_coins(df, coins_to_keep):
    return df[df['Coin'].isin(coins_to_keep)]

def assetFormat(df, keep):
    if keep:
        df = keep_coins(df, ['USD', 'USDT', 'USDC', 'EUR', 'BUSD', 'ZUSD'])
    else:
        df = remove_coins(df, ['USD', 'USDT', 'USDC', 'EUR', 'BUSD', 'ZUSD'])
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account']]

    return df

def aggCoins(df, keep):
    if keep:
        df = keep_coins(df, ['USD', 'USDT', 'USDC', 'EUR', 'BUSD', 'ZUSD'])
        df['QTY'] = df['QTY'].astype(float)
        df = df.groupby(['Coin']).agg({
                'Coin':'last',
                'QTY':'sum',
                'USDValue':'sum',
            })
        return df
    else:
        df = remove_coins(df, ['USD', 'USDT', 'USDC', 'EUR', 'BUSD', 'ZUSD'])
        df['QTY'] = df['QTY'].astype(float)
        df['Asset'] = df.apply(lambda row: row['QTY'] if pd.isna(row['Leverage']) else np.nan, axis=1)
        df['Position'] = df.apply(lambda row: row['QTY'] if not pd.isna(row['Leverage']) else np.nan, axis=1)
        df['Asset'] = df['Asset'].astype(float)
        df['Position'] = df['Position'].astype(float)
        df['QTY'] = df['QTY'].astype(float)
        df['USDValue'] = df['USDValue'].astype(float)
        df = df.groupby(['Coin']).agg({
                'Coin':'last',
                'Asset':'sum',
                'Position':'sum',
                'QTY':'sum',
                'USDValue':'sum',
            })
        df['Price'] = df.apply(netPrice, axis=1)
        df['USDValue'] = df['QTY'].astype(float) * df['Price'].astype(float)
        df = df[["Coin", "Asset", "Position", "QTY", "Price", "USDValue"]]
        return df

def netPrice(row):
    try:
        return Binance.coinPrice(row['Coin'])
    except:
        return 0

def balance(bal, stakedAss):
    totalOver = totalBalance(bal)
    bal = [{'Total Overall': totalOver, 'Ave Staked Dur':stakedAss[0]['Average Staking Duration'], 'Staked Value':stakedAss[0]['Sum USDValue']}]
    bal = pd.DataFrame(bal)
    return bal

def agg(df, org):
    df['USDValue'] = df['USDValue'].astype(float)
    if org == 'PositionUSDValue':
        df['USDValue_abs'] = df['USDValue'].abs()

    try:
        df = df.groupby(['Exchange', 'Account']).agg({
            'USDValue': 'sum',
            'MaintMargin':'last',
            'USDValue_abs':'sum'
        }).reset_index()
    except:
        df = df.groupby(['Exchange', 'Account']).agg({
            'USDValue': 'sum',
        }).reset_index()
        df['MaintMargin'] = 0

    df.rename(columns={'USDValue': org}, inplace=True)
    return df

def calcLeverage(row):
    try:
        return (row['PositionAbsolute']/row['WalletUSDValue'])
    except:
        return 0

def calculation(row):
    try:
        B3 = float(row['PositionAbsolute'])
        B4 = float(row['WalletUSDValue'])
        B5 = float(row['MaintMargin'])

        return ((B3*(1+B4/B3)/(1+B5/B3))/B3-1)*100
    except:
        return 0

def leverage(pos, bal):
    #print('\n###########################################\n')
    #print(pos)
    aggBal = agg(bal, 'WalletUSDValue')
    aggPos = agg(pos, 'PositionUSDValue')
    #print(aggPos)
    df = pd.concat([aggBal, aggPos], ignore_index=True)
    #print(df) # Hercle is still present here
    try:
        df.loc[(df['Exchange'] == 'Hercle') & (df['Account'] == 'Earn'), 'Account'] = 'USDT-M'
    except:
        print("Couldn't change hercle ya bish")
    df = df.groupby(['Exchange', 'Account']).agg({
        'WalletUSDValue': 'last',
        'PositionUSDValue':'last',
        'MaintMargin':'last',
        'USDValue_abs':'last',
    }).reset_index()
    #print(df) #still there
    df['PositionAbsolute'] = abs(df['PositionUSDValue'].astype(float))
    df['Leverage_PUV'] = df.apply(calcLeverage, axis=1)
    #print(df) #both there
    df = df.dropna(subset=['PositionUSDValue'])
    #print(df) #ones gone
    df = df[df['Account'] == 'USDT-M']
    df['LiqMove'] = df.apply(calculation, axis=1)
    df['PositionAbsolute'] = df['USDValue_abs']
    df['WalletCoinValue'] = df.apply(net_lev, axis=1)

    #This will get the highest USDValue per postion and its contract
    unique_ex = pos["Exchange"].unique()

    rows = []

    def remove_comma(row):
        try:
            x = row['USDValue'].replace(",","")
            return x
        except:
            return row['USDValue']

    for ex in unique_ex:
        #df_second = pos[(pos["Exchange"] == ex) & (pos['Account'] == "USDT-M")]
        df_second = pos[(pos["Exchange"] == ex) & (pos['Account'].isin(["USDT-M", "Earn"]))]


        df_second['USDValue'] = pos.apply(remove_comma, axis=1)

        df_second["USDValue"] = df_second["USDValue"].astype(float)

        df_second["USDValue"] = df_second["USDValue"].abs()

        df_second["USDValue"] = df_second["USDValue"].fillna(0)

        max_value = df_second['USDValue'].idxmax()

        #df_second = df_second.fillna(0.00)

        #print(max_value)

        row = {"Contract":df_second.loc[max_value].to_dict()['Contract'], "HighestPos":df_second.loc[max_value].to_dict()['USDValue'], "Exchange":df_second.loc[max_value].to_dict()['Exchange']}

        rows.append(row)

    rows = pd.DataFrame(rows)

    df = pd.merge(df, rows, on='Exchange', how='left')

    df.loc[df['Exchange'] == 'Hercle', 'MaintMargin'] = df[df['Exchange'] == 'Hercle'].apply(formula, axis=1)

    df['BP%'] =((df['WalletUSDValue'].astype(float) - df['MaintMargin'].astype(float)) / df['HighestPos']) * 100

    df['MM%'] = (df['MaintMargin'].astype(float) / df['WalletUSDValue'].astype(float)) * 100 

    df['Leverage_PA'] = df['PositionAbsolute'].astype(float) / df['WalletUSDValue'].astype(float)

    df =df[['Exchange', 'Account', 'WalletUSDValue', 'PositionUSDValue', 'PositionAbsolute', 'Leverage_PUV', 'Leverage_PA', 'MaintMargin', 'LiqMove', 'WalletCoinValue', 'Contract', 'HighestPos', 'BP%', 'MM%']]
    #print('\n###########################################\n')
    #daf.loc[df['Exchange'] == 'Hercle', 'MaintMargin'] = df[df['Exchange'] == 'Hercle'].apply(formula, axis=1)
    return df

def formula(row):
    return float(row['PositionAbsolute']) / 10

def net_lev(row):
    [sys.path.append(directory) for directory in ['config', 'Exchange_Functions']]
    import keys, Binance
    keys = {'Binance_Sub1':[keys.binance_sub1_key, keys.binance_sub1_secret], 'Binance':[keys.binance_key, keys.binance_secret], 'Binance_Sub4':[keys.binance_sub4_key, keys.binance_sub4_secret], 'Bybit':[keys.bybit_key, keys.bybit_secret], 'Bybit_HR':[keys.bybit_hr_key, keys.bybit_hr_secret], 'Bybit_Sub1':[keys.bybit_sub_1_key, keys.bybit_sub_1_secret]}
    if row['Exchange'][:3] == "Bin":
        try:
            x = keys[row['Exchange']]
            y = Binance.net_lev(x[0], x[1])
            return y
        except:
            return 0
    elif row['Exchange'][:3] == "Byb":
        try:
            x = keys[row['Exchange']]
            y = Bybit.net_lev(x[0], x[1])
            return y

        except:
            return 0
    else:
        return 0

def breakdown(df):
    #print(df.to_dict(orient='records'))
    allHeaders = ['Exchange', 'USDT-M', 'SPOT', 'MARGIN', 'EARN', 'COIN-M', 'Loan', 'Total']
    df = agg(df, 'USDValue')
    df = df.pivot(index='Exchange', columns='Account', values='USDValue')
    df = df.reset_index()
    df.columns.name = None
    df = df.fillna(0.0)
    headers = df.columns.tolist()
    for i in headers:
        if i != 'Exchange':
            df[i] = pd.to_numeric(df[i], errors='coerce')
    df['Total'] = df.iloc[:, 1:].sum(axis=1)
    headers = df.columns.tolist()
    allHeaders_set = set(allHeaders)
    headers_set = set(headers)
    difference_list = list(allHeaders_set.symmetric_difference(headers_set))
    for i in difference_list:
        df[i] = 0.0
    df.loc['Totals'] = df.sum(numeric_only=True)
    df.at['Totals', 'Exchange'] = 'Totals'
    df = df[allHeaders]
    df = df.fillna(0.0)

    return df

def calcFundingAmount(row):
    try:
        return (row['Funding'])*(row['USDValue']*-1)
    except:
        return '0.0'

#def fundValue(row, funding):
#    print(row)
#    print('\n##########\n')
#    print(funding)
#    try:
#        ex = row['Exchange'].split('_')[0]
#    except:
#        ex = row['Exchange']
#    funding = funding[(funding['Exchange'] == ex) & (funding['Coin'] == row['Coin']) & (funding['Account'] == row['Account'])]
#    try:
#        if len(funding['Funding']) > 1:
#            funding = float(funding['Funding'].iloc[-1])
#        else:
#            funding = float(funding['Funding'])
#        return funding
#    except:
#        return 0

def fundValue(row, funding):
    try:
        try:
            if row['Contract'] == "ETHUSD_240927" or row['Contract'] == "DOTUSD_240927":
                return 0.0
        except:
            pass
        #coin = row['Coin']
        coin = row['Contract']
        exchange = row['Exchange'].split('_')[0]  # Assuming exchange name is before the underscore
        #value = funding.loc[funding['Coin'] == coin, exchange].values[0]
        #value = funding.loc[(funding['Coin'] == coin) & (funding['Exchange'] == exchange), 'Funding'].values[0]
        value = funding.loc[(funding['Coin'] == coin) & (funding['Exchange'] == exchange), 'Funding']
        if len(value) == 0:
            try:
                value = funding.loc[(funding['Coin'] == coin) & ("Binance" == exchange), 'Funding'].values[0]
                return value
            except:
                pass
        value = value.values[0]
        return value
    except Exception as e:
        #print(f"379 An error occurred: {e}")
        return 0.0

def funding(df):
    fund = pd.DataFrame(fundStore.funding)
    fund.rename(columns={'Symbol': 'Coin'}, inplace=True)
    df['Funding'] = df.apply(lambda row: fundValue(row, fund), axis=1)
    df['Funding Amount'] = df.apply(calcFundingAmount, axis=1)
    df = df.sort_values(by='Coin')
    df['Funding'] = df['Funding'].astype(float)*100
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'MarkPrice', 'Funding', 'Funding Amount']]
    return df

def consolidate_positions(df):
    df_back = df.copy()
    df.dropna(axis=0, inplace=True)
    df = df[~df['Contract'].str.endswith('_PERP')]
    df_back = df_back.merge(df, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    df['MarkPrice'] = df['MarkPrice'].astype(float)
    df['LiqPrice'] = df['LiqPrice'].astype(float)
    df = df.groupby(['Exchange', 'Coin']).agg({
        'QTY': 'sum',
        'USDValue': 'sum',
        'Leverage': 'sum',
        'MarkPrice': 'sum',
        'LiqPrice': 'sum',
        'LiqRisk': 'first',
        'Account': 'first',
        'Contract': 'first',
    }).reset_index()
    df = pd.concat([df_back, df], axis=0)
    return df

def coinM(df):
    df1 = df[df['Account'] == 'COIN-M']
    df2 = df[df['Account'] == 'Coin-M']


    df = pd.concat([df1, df2], axis=0)

    df = consolidate_positions(df)

    Bdf = df[df['Leverage'].isna()]
    Adf = df[df['Leverage'].notna()]

    Adf['MarkPrice'] = Adf['MarkPrice'].astype(float)

    Adf['LiqPrice'] =Adf['LiqPrice'].astype(float)
    Bdf['LiqPrice'] =Bdf['LiqPrice'].astype(float)

    #print(Adf)
    #print(Bdf)

    Bdf = Bdf.groupby(["Exchange", "Coin"]).agg({
        'QTY': 'sum',
        'USDValue': 'sum',
        'Leverage': 'sum',
        'MarkPrice': 'sum',
        'LiqPrice': 'sum',
        'LiqRisk': 'first',
        'Account': 'first',
        'Contract': 'first',
    }).reset_index()

    Adf = Adf.groupby(["Exchange", "Coin"]).agg({
        'QTY': 'sum',
        'USDValue': 'sum',
        'Leverage': 'sum',
        'MarkPrice': 'sum',
        'LiqPrice': 'sum',
        'LiqRisk': 'first',
        'Account': 'first',
        'Contract': 'first',
    }).reset_index()

    df = Adf.merge(Bdf[['Exchange', 'Coin', 'QTY', 'USDValue']], on=['Exchange', 'Coin'], how='left')
    #print(df)

    df.rename(columns={'QTY_x': 'QTY', 'USDValue_x': 'USDValue'}, inplace=True)
    df.rename(columns={'QTY_y': 'CollQTY', 'USDValue_y': 'CollUSD'}, inplace=True)
    df['Lever'] = abs(df['USDValue'].astype(float)/df['CollUSD'].astype(float))
    df['Contract'] = df['Coin']
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'CollQTY', 'CollUSD', 'Exchange', 'Account', 'Lever', 'MarkPrice', 'LiqPrice', 'LiqRisk']]
    df = df.dropna()
    if len(df) == 0:
        df = pd.DataFrame([{"Coin": "NaN","Contract": "NaN","QTY": "0.00","USDValue": "0.00","CollQTY": "0.00","CollUSD": "0.00","Exchange": "NaN","Account": "COIN-M","Lever": "0.00","MarkPrice": "0.00","LiqPrice": "0.00","LiqRisk": "1.00"}])
    return df

def aggFunding(df):
    df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')
    df['USDValue'] = pd.to_numeric(df['USDValue'], errors='coerce')
    df['Funding'] = pd.to_numeric(df['Funding'], errors='coerce')
    df['Funding Amount'] = pd.to_numeric(df['Funding Amount'], errors='coerce')

    df = df.groupby(['Coin']).agg({
        'Contract':'last',
        'QTY':'sum',
        'USDValue':'sum',
        'Funding':'sum',
        'Funding Amount':'sum',
    }).reset_index()
    return df

def create_new_column(row):
    lock = {'ATOM':21,'AVAX':14,'CARTESI':2,'FLOW':7,'NEAR':4,'ONE':7,'TEZOS':0,'ROSE':14,'SECRET':21,'KAVA':21, 'KSM':7, 'ATOM.S':0, 'DOT.S':0, 'DOT28.S':28, 'GRT28.S':28, 'LPT':9, 'XTZ':7, 'TEZOS':7}
    try:
        return lock[row['Contract']]
    except:
        return 0 #
    
def cexAsset(df):
    cexAssets = df[(df['Exchange'] != 'FireBlocks')]
    cexAssets = cexAssets[(cexAssets['Exchange'] != 'FireBlocks_Cold')]
    cexAssets = cexAssets[(cexAssets['Exchange'] != 'FireBlocks_VAL')]
    cexAssets = cexAssets[(cexAssets['Exchange'] != 'FireBlocks_Bond')]
    return cexAssets

def calc(df):
    df['Lockup'] = df.apply(create_new_column, axis=1)
    df['invis'] = df['USDValue'].astype(float)*df['Lockup'].astype(float)
    USDSum = df['USDValue'].sum()
    invisSum = df['invis'].sum()
    df = df.drop(columns=['invis'])
    calc = invisSum/USDSum
    calc = f"{calc:.2f}"
    USDSum = '{:,.2f}'.format(USDSum)
    calc = [{'Average Staking Duration':calc, 'Sum USDValue':USDSum}]
    return calc

def calc_yield(df):
    df['tmp'] = df['USDValue'].astype(float) * df['Reward'].astype(float)
    USDSum = df['USDValue'].sum()
    TMPSum = df['tmp'].sum()
    df = df.drop(columns=['tmp'])
    calc = TMPSum / USDSum
    calc = f"{calc:.4f}"
    return calc

def format(df, formatfields2, formatfields6):
    try:
        df.fillna('nan', inplace=True)
        df.fillna('None', inplace=True)
    except:
        pass
    try:
        df = df.sort_values(by='Coin')
    except:
        pass
    try:
        for i in formatfields2:
            try:
                df[i] = df[i].astype(float)
                df[i] = df[i].apply(lambda x: f'{x:,.2f}')
            except:
                pass
    except:
        pass
    try:
        for i in formatfields6:
            try:
                df[i] = df[i].astype(float)
                df[i] = df[i].apply(lambda x: f'{x:,.4f}')
            except:
                pass
    except:
        pass
    return df

def staked_assets(staked):
    def format_value(row):
        try:
            return row['USDValue'].replace(',', '')
        except:
            return row['USDValue']

    df = pd.DataFrame(staked)
    df['USDValue'] = df.apply(format_value, axis=1)
    df['USDValue'] = df['USDValue'].astype(float)
    USDSum = df['USDValue'].sum()
    df['Reward'] = df.apply(reward_map, axis=1)
    df['%'] = (df['USDValue'] / USDSum) * 100

    return df

def reward_map(row):
    reward_mapp = {"ATOM":0.15183, "ATOM.S":0.068, "CARTESI":0.14418, "DOT.S":0.062, "DOT28.S":0.172, "FLOW":0.0792, "KSM":0.1845, "KSM.S":0.078, "MINA.S":0.152, "NEAR":0.0594, "ONE":0.0702, "TEZOS":0.14, "BTC":0, "TAO":0.145, "GRT28.S":0.11, "LPT":0.4604, "MINA.F":0.152, "MINA.F":0.152, "XTZ":0.1197, "TEZOS":0.1197}
    try:
        return reward_mapp[row['Contract']]
    except:
        return 123

def return_date(row):
    date = row['symbol'].split("_")
    date_obj = datetime.strptime(str(date[1]), "%y%m%d")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    return formatted_date

def days_to_mature(row):
    #tz = pytz.timezone("Europe/London")
    current_date = datetime.now()
    #current_date = tz.localize(current_date)
    datetime_mature = datetime.strptime(row['Maturity Date'], "%Y-%m-%d")
    days_mature = (datetime_mature-current_date).days+1
    return days_mature

def ann_yield(row):
    try:
        ann_days = float(row['Days to Maturity']) / 365
        ann_spread = float(row['Spread %']) / ann_days
        return ann_spread
    except Exception as e:
        print(f"Error ann_yield for {row['Symbol']}: {e}")
        return 1

def offer_spread():
    r = requests.get("https://dapi.binance.com/dapi/v1/premiumIndex").json()
    df = pd.DataFrame(r)
    df = df[~df['symbol'].str.endswith('_PERP')]
    df['Symbol'] = df['symbol']
    df['Spread'] = df['markPrice'].astype(float) - df['indexPrice'].astype(float)
    df['Spread %'] = df['Spread'] / df['indexPrice'].astype(float)
    df['Maturity Date'] = df.apply(return_date, axis=1)
    df['Days to Maturity'] = df.apply(days_to_mature, axis=1)
    df = df[df['Days to Maturity'] != 0]
    df['Annualised Yield'] = df.apply(ann_yield, axis=1)
    df = df[['Symbol', 'Spread', 'Spread %', 'Days to Maturity', 'Annualised Yield']]
    df = df.sort_values(by='Symbol')
    return df

def aggFundingFees(report_df):
    some_list = []
    df = report_df.copy()
    df['TIME'] = pd.to_datetime(df['TIME'])
    dfs_by_day = {day: group for day, group in df.groupby(df['TIME'].dt.date)}
    for i in dfs_by_day:
        dfs_by_day[i]['SIZE'] = dfs_by_day[i]['SIZE'].astype(float)
        dfNew = dfs_by_day[i].groupby(['SYMBOL', "TIME"]).agg({
            'TYPE':'last',
            'FEE':'sum',
        }).reset_index()
        some_list.append(dfNew)
    df_slingShot = pd.concat(some_list, ignore_index=True)
    #df_slingShot['TIME'] = df_slingShot['TIME'].astype(str)
    df_slingShot = df_slingShot.sort_values(by='SYMBOL')
    df_slingShot['TIME'] = df_slingShot['TIME'].astype(str)
    #df_slingShot = df_slingShot.sort_values(by='VENUE')
    df_slingShot = df_slingShot[['TIME', 'SYMBOL', 'TYPE', 'FEE']]
    #df_slingShot.sort_values(by="TIME")
    #df_slingShot = df_slingShot[['VENUE', 'SYMBOL', 'TYPE', 'SIZE', 'CURRENCY']]
    return df_slingShot

def agg_funding_time(report_df):
    report_df['SIZE'] = report_df['SIZE'].astype(float)
    df = report_df.groupby(["TIME"]).agg({
            "SIZE":"sum",
            "FEE":"sum",
        }).reset_index()

    df = df.sort_values(by="TIME", ascending=False)

    return df

def breakdown_const(df):
    df = df.fillna(0.0)
    try:
        df.sort_values(by="Account")
        df.sort_values(by="Exchange")
    except:
        pass
    df['QTY'] = df['QTY'].astype(float)#.round(2)
    df['USDValue'] = df['USDValue'].astype(float)#.round(2)
    df['Price'] = df.apply(breakdown_price, axis=1)
    df = df[['Coin', 'Contract', 'QTY', 'USDValue', 'Exchange', 'Account', 'Price']]
    return df

def breakdown_price(row):
    try:
        if row['Coin'] != "USDT":
            r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+row['Coin'].upper()+'USDT').json()['price']
            float_r = float(r)
            return float_r #round(float_r, 2)
        elif row['Coin'] == "USDT":
            r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+row['Coin'].upper()+'USD').json()['price']
            float_r = float(r)
            return float_r #round(float_r, 2)
    except:
        return 0

def get_spread(row, spread_df):
    matched_row = spread_df[spread_df['Symbol'].isin([row['Contract']])]
    match = matched_row.to_dict(orient='records')
    return match[0]['Spread']

def get_entry_spread(row):
    try:
        entry_price_manuel = {'ETHUSD_240628':3820.93, 'BTCUSD_240329':71309.47, 'BTCUSD_240628':65456.20}
        return float(row['EntryPrice']) - float(entry_price_manuel[row['Contract']])
    except:
        return 0

def spreading(coinM, spread_offer, net_pos):
    df = pd.DataFrame([{"TEST FIELD 1":"In progress", "TEST FIELD 2":"In progress", "TEST FIELD 3":"In progress"}, {"TEST FIELD 1":"In progress", "TEST FIELD 2":"In progress", "TEST FIELD 3":"In progress"}])

    return df

def type_mapping(row):
    carry_coins = {'BTCUSD_250328', 'BTCUSD_250627', 'BTCUSD_250627', 'ETHUSD_250328', 'XRPUSD_250328', 'SOLUSD_250328'}
    if row['Contract'] in carry_coins:
        return "Carry"
    else:
        return "Hedge"

mid = time.time()
print(f"Loaded functions in: {mid-start} seconds")

pos = allPositions()
bal = allBalance()

#print(pos.to_dict(orient='records'))

df = BalPos(bal, pos)

#breakdown_constructor = bal
#breakdown_constructor = breakdown_const(breakdown_constructor)

fundingDF = funding(pos)
assets = assetFormat(bal, False)
cexAsset = cexAsset(assets)
FBA = assets[(assets['Exchange'] == 'FireBlocks') | (assets['Exchange'] == 'FireBlocks_Cold') | (assets['Exchange'] == 'FireBlocks_VAL') | (assets['Exchange'] == 'FireBlocks_Bond') | (assets['Account'] == 'EARN')]
stakedAsset = FBA[FBA['Exchange'] != 'FireBlocks_Cold']
#stakedAsset = stakedAsset[stakedAsset['QTY'].astype(float) >= 10]

stakedAsset = stakedAsset[
    (stakedAsset['QTY'].astype(float) >= 10) | 
    ((stakedAsset['Contract'] == 'BTC') & (stakedAsset['QTY'].astype(float) > 1))
]


try:
    falconx_staking = falconxData[(falconxData['id'] == 'staking') | (falconxData['Coin'] == "TAO")]
    falconx_staking['QTY'] = falconx_staking['QTY'].astype(float)
    falconx_staking = falconx_staking.groupby(['Coin', 'Contract']).agg({
        'Coin':'last',
        'Contract':'last',
        'QTY':'sum',
        'USDValue':'sum',
        'Exchange':'last',
        'Account':'last'
    })
    stakedAsset = pd.concat([falconx_staking, stakedAsset], ignore_index=True)
except:
    pass

stakedAsset = stakedAsset.groupby(['Coin', 'Contract']).agg({
            'Coin':'last',
            'Contract':'last',
            'QTY':'sum',
            'USDValue':'sum',
            'Exchange':'last',
            'Account':'last'
        })
calc = calc(stakedAsset)
stakedAsset = stakedAsset.drop(columns=['invis'])
stakedAsset = staked_assets(stakedAsset)
avg_stake_yield = calc_yield(stakedAsset)
stakedAsset = stakedAsset.drop("tmp", axis='columns')
stables = assetFormat(df, True)
coinM = coinM(df)
fundingAgg = aggFunding(fundingDF)
breakdown = breakdown(bal)
leverage = leverage(pos, bal)
balance = balance(bal, calc)
aggCoinT = aggCoins(bal, True)
aggCoinF = aggCoins(df, False)
nextFunding = fundingDF['Funding Amount'].sum()
nextFunding = '{:,.2f}'.format(nextFunding)
#FBA = FBA[FBA['Account'] != 'EARN']
reporting = report.build_csv()
rewards = report.get_rewards()
agg_funding_fee = aggFundingFees(reporting)
time_funding = agg_funding_time(reporting)
breakdown_constructor = bal
breakdown_constructor = breakdown_const(breakdown_constructor)

try:
    offer_spread_df = offer_spread()
except Exception as e:
    print(f"ERROR UR LOOKING FOR {e}")

spread_values = spreading(coinM, offer_spread_df, aggCoinF)

pos['Pos Type'] = pos.apply(type_mapping, axis=1)

bd_const = breakdown_constructor.to_dict(orient='records')
bd_const_raw = breakdown_constructor.to_dict(orient='records')

breakdown_constructor = f"breakdown_constructor = {format(bd_const, ['QTY', 'USDValue', 'Price'], [])}"
breakdown_constructor_raw = f"breakdown_constructor_raw = {format(bd_const_raw, [], [])}"
avg_stake_yield = f"avg_stake_yield = {avg_stake_yield}"
rewards = 'rewards = '+str(format(rewards, ['SIZE', 'CUMULATIVE'], []).to_dict(orient='records'))
reporting = 'report = '+str(format(reporting, ['SIZE', 'FEE'], []).to_dict(orient='records'))
funding = 'funding = '+str(format(fundingDF, ['QTY', 'USDValue', 'MarkPrice'], ['Funding', 'Funding Amount']).to_dict(orient='records'))
aggfunding = 'aggfunding = '+str(format(fundingAgg, ['QTY', 'USDValue', 'MarkPrice'], ['Funding', 'Funding Amount']).to_dict(orient='records'))
breakdown = 'breakdown = '+str(format(breakdown, ['USDT-M', 'SPOT', 'MARGIN', 'EARN', 'COIN-M', 'Loan', 'Total'], []).to_dict(orient='records'))
leverage = 'leverage = '+str(format(leverage, ['WalletUSDValue', 'PositionUSDValue', 'PositionAbsolute', 'Leverage_PUV', 'MaintMargin', 'LiqMove', 'WalletCoinValue', 'HighestPos', 'BP%', 'MM%', 'Leverage_PA'], []).to_dict(orient='records'))
balance = 'balance = '+str(format(balance, ['Initial Balance', 'Total Overall', 'Total Invested'], []).to_dict(orient='records'))
coinM = f"coinM = {str(format(coinM, ['QTY', 'USDValue', 'CollQTY', 'CollUSD', 'Lever', 'LiqRisk'], ['MarkPrice', 'LiqPrice']).to_dict(orient='records'))}"
stables = 'stables = '+str(format(stables, ['QTY', 'USDValue'], []).to_dict(orient='records'))
pos = pos.drop(columns=['MaintMargin', 'Funding', 'Funding Amount'])
positions = 'position = '+str(format(pos, ['QTY', 'USDValue', 'LiqRisk', 'USDValue_abs', 'UnrealisedProfit'], ['MarkPrice', 'LiqPrice']).to_dict(orient='records'))
aggStabs = 'aggStabs = '+str(format(aggCoinT, ['QTY', 'USDValue'], []).to_dict(orient='records'))
aggAssets = 'aggAssets = '+str(format(aggCoinF, ['QTY', 'USDValue', 'Position', 'Price', 'Asset'], []).to_dict(orient='records'))
cexAsset = f"cexAss = {format(cexAsset, ['QTY', 'USDValue'], []).to_dict(orient='records')}"
fba = f"fba = {format(pd.DataFrame(fireBlocksData), ['QTY', 'USDValue'], []).to_dict(orient='records')}"
staked = f"staked = {format(stakedAsset, ['QTY', 'USDValue'], ['%']).to_dict(orient='records')}"
calc = f"calc = {calc}"
nextFund = f"nextFund = {str([{'nextFunding':nextFunding}])}"
spread = f"spread = {str(format(offer_spread_df, [], ['Spread', 'Spread %', 'Annualised Yield']).to_dict(orient='records'))}"
agg_funding_fees = f"agg_funding_fee = {str(format(agg_funding_fee, ['SIZE', 'FEE'], []).to_dict(orient='records'))}"
time_agg_funding = f"time_agg_funding = {str(format(time_funding, ['SIZE', 'FEE'], []).to_dict(orient='records'))}"
spread_values = f"spreading = {format(spread_values, [], []).to_dict(orient='records')}"
##okxLoan = f"okx_loan = {okx_loan_data}"


#timeZone = timezone(timedelta(hours=1))
#current_time = datetime.now(timeZone)
current_time = datetime.now(pytz.timezone('Europe/London'))
currentTime = current_time.strftime('%H:%M')
elTime = current_time.strftime('%d/%m/%Y')
currentTime = f"time = '{str(currentTime)}_{str(elTime)}'"

with open ('html/tmp.py', 'w', encoding='utf-8') as f:
    ##f.write(okxLoan)
    ##f.write('\n')
    f.write(breakdown_constructor_raw)
    f.write('\n')
    f.write(spread_values)
    f.write('\n')
    f.write(breakdown_constructor)
    f.write('\n')
    f.write(time_agg_funding)
    f.write('\n')
    f.write(agg_funding_fees)
    f.write('\n')
    f.write(spread)
    f.write('\n')
    f.write(rewards)
    f.write('\n')
    f.write(reporting)
    f.write('\n')
    f.write(currentTime)
    f.write('\n')
    f.write(str(nextFund))
    f.write('\n')
    f.write(str(calc))
    f.write('\n')
    f.write(str(staked))
    f.write('\n')
    f.write(str(fba))
    f.write('\n')
    f.write(str(cexAsset))
    f.write('\n')
    f.write(str(stables))
    f.write('\n')
    f.write(str(positions))
    f.write('\n')
    f.write(str(balance))
    f.write('\n')
    f.write(str(aggStabs))
    f.write('\n')
    f.write(str(aggAssets))
    f.write('\n')
    f.write(str(leverage))
    f.write('\n')
    f.write(str(breakdown))
    f.write('\n')
    f.write(str(funding))
    f.write('\n')
    f.write(str(aggfunding))
    f.write('\n')
    f.write(str(coinM))
    f.write('\n')
    f.write(str(avg_stake_yield))

end=time.time()
print('Time taken to run: '+str(end-start))
