import sys, datetime, time, threading
import pandas as pd

#start = time.time()

sys.path.append('html/')
sys.path.append('Exchange_Functions/')
sys.path.append('config/')

import tmp
import keys
import Binance as b
import Bybit as by
import Gate as g
import fb_rewards as fb

def symb(row):
    if row["symbol"][-1] == "T":
        formatted = row["symbol"].replace("USDT", "")
    elif row["symbol"][-1] == "P":
        formatted = row["symbol"].replace("USD_PERP", "")
    else:
        formatted = row["symbol"]
    return formatted

def binance_price(row):
    if row['CURRENCY'] != "USDT":
        try:
            """
            TO DO:
            Need to add a function to replace the get price function for each exchange
            It just needs to read the positions table once and use the mark prices from there
            ONLY READ AND CALL POSITIONS ONCE
            """
            #print(tmp.position)
            df = pd.DataFrame(tmp.position)
            #print(row['CONTRACT'], row['EXCHANGE'])
            #print(df)
            #matched_row = df[(df['Contract'] == row['CONTRACT']) & (df['Exchange'] == row['EXCHANGE'])]
            matched_row = df[(df['Contract'] == row['CONTRACT']) & (df['Exchange'] == row['EXCHANGE'])].to_dict(orient='records')[0]['MarkPrice']
            #print(matched_row, '\n##################################################')
            #price = b.get_binance_current_price(row['SYMBOL'], row["CURRENCY"])
            return float(matched_row) * float(row['SIZE'])
        except:
            return 0
            #print('\n################################################')
    else:
        return float(row['SIZE'])

def binanceFunding(concat, api_key, api_secret, exchange):
    try:
        fund = b.binance_send_signed_request('https://fapi.binance.com', "GET", "/fapi/v1/income", api_key, api_secret, payload={"limit":1000, "incomeType":"FUNDING_FEE"})
        #fund = b.binance_send_signed_request('https://fapi.binance.com', "GET", "/fapi/v1/income", api_key, api_secret, payload={"limit":1000})
        #print(f"{exchange}\n{fund}\n################################################################\n")
        df1 = pd.DataFrame(fund)
        

        fund2 = b.binance_send_signed_request('https://dapi.binance.com', "GET", "/dapi/v1/income", api_key, api_secret, payload={"limit":1000})
        #print(f"{fund2}\n################################################################\n")
        df2 = pd.DataFrame(fund2)

        #print(df2)
        try:
            df2['time'] = df2['time'].astype(float)
            timeStop = (float(time.time()) - 259200) * 1000
            df2 = df2[(df2['time'] > timeStop)]
        except:
            pass

        #try:
        #    df1['time'] = df1['time'].astype(float)
        #    timeStop = (float(time.time()) - 86400) * 1000
        #    df1 = df1[(df1['time'] > timeStop)]
        #except:
        #    pass

        #print(timeStop, df2)
        df = pd.concat([df1, df2], axis=0)
        df = df[(df['incomeType'] == 'FUNDING_FEE')]
        if concat:
            df['income'] = df['income'].astype(float)
            df = df.groupby(['symbol']).agg({
                    'income':'sum',
                }).reset_index()
        df['VENUE'] = "Binance"
        df['EXCHANGE'] = exchange
        df['TYPE'] = df['incomeType']
        df['SIZE'] = df['income']
        df['TIME'] = df['time'].astype(float)
        df['CURRENCY'] = df['asset']
        #df.rename(columns={'symbol': 'SYMBOL'}, inplace=True)
        df['CONTRACT'] = df['symbol']
        df['SYMBOL'] = df.apply(symb, axis=1)
        df['FEE'] = df.apply(binance_price, axis=1)
        df = df[['TIME', 'VENUE', 'SYMBOL', 'TYPE', 'SIZE', 'CURRENCY', 'EXCHANGE', 'CONTRACT', 'FEE']]
        #df.to_csv(f"/home/ubuntu/csv/{exchange}.csv")
        return df
    except Exception as e:
        print(f"Binance not added account {exchange}\nError: {e}\n##########################\n")

#binanceFunding(False, keys.binance_key, keys.binance_secret, "Binance")

def bybit_price(row):
    if row['CURRENCY'] != "USDT":
        try:
            df = pd.DataFrame(tmp.position)
            matched_row = df[(df['Contract'] == row['CONTRACT']) & (df['Exchange'] == row['EXCHANGE'])].to_dict(orient='records')[0]['MarkPrice']
            #price = by.get_bybit_current_price(row['SYMBOL'])
            return float(matched_row) * float(row['SIZE'])
        except:
            return 0
    else:
        return float(row['SIZE'])

def bybitFunding(concat, api_keys, api_secret, exchange, endtime):
    try:
        fund = by.get_v5_fundingFees(api_keys, api_secret, endtime)
        #print(f"{fund}\n################################################################\n")
        df = pd.DataFrame(fund['result']['list'])

        #df.to_csv("bybit_funding_fees.csv")
        if concat:
            df['change'] = df['change'].astype(float)
            df = df.groupby(['symbol']).agg({
                    'change':'sum',
                }).reset_index()
        df['VENUE'] = "Bybit"
        df['EXCHANGE'] = exchange
        df['TYPE'] = 'FUNDING_FEE'
        df['SIZE'] = df['change']
        df['TIME'] = df['transactionTime'].astype(float)
        #df.rename(columns={'symbol': 'SYMBOL'}, inplace=True)
        df['CONTRACT'] = df['symbol']
        df['SYMBOL'] = df.apply(symb, axis=1)
        df['CURRENCY'] = df['currency']
        df['FEE'] = df.apply(bybit_price, axis=1)
        df = df[['TIME', 'VENUE', 'SYMBOL', 'TYPE', 'SIZE', 'CURRENCY', 'EXCHANGE', 'CONTRACT', 'FEE', 'type']]
        #print(df)
        #df.to_csv(f"/home/ubuntu/csv/{exchange}.csv")
        return df
    except Exception as e:
        print(f"Bybit not added account {exchange}\nError: {e}\n##########################\n")

#bybitFunding(False, keys.bybit_key, keys.bybit_secret, "Bybit", int(time.time()*1000))

def run_bybit(concat, api_keys, api_secret, exchange, endtime):
    first_table = bybitFunding(concat, api_keys, api_secret, exchange, endtime)
    #print(first_table)
    second_time = first_table.iloc[len(first_table)-1]["TIME"] + 10
    second_table = bybitFunding(concat, api_keys, api_secret, exchange, second_time)
    #print(second_table)
    third_time = second_table.iloc[len(second_table)-1]["TIME"] + 10
    third_table = bybitFunding(concat, api_keys, api_secret, exchange, third_time)
    #print(third_table)
    df = pd.concat([first_table, second_table, third_table], axis=0)

    df = df[df['type'] == 'SETTLEMENT']

    df = df[['TIME', 'VENUE', 'SYMBOL', 'TYPE', 'SIZE', 'CURRENCY', 'EXCHANGE', 'CONTRACT', 'FEE']]

    #df.to_csv("/home/ubuntu/bybit_dupe.csv")
    #pd.set_option('display.max_rows', None)  # Show all rows
    #pd.set_option('display.max_columns', None)
    #print(df.duplicated())
    #print(df)

    #print(df.iloc[48])
    #print(df.iloc[3])
    df.drop_duplicates(subset=['VENUE', 'SYMBOL', 'SIZE', 'CURRENCY', 'EXCHANGE', 'CONTRACT'])

    return df

#run_bybit(False, keys.bybit_key, keys.bybit_secret, "Bybit", int(time.time()*1000))
#run_bybit(False, keys.bybit_sub_1_key, keys.bybit_sub_1_secret, "Bybit", int(time.time()*1000))

def split_text(row, index):
   return row['text'].split('_')[index]

def gate_price(row):
    if row['CURRENCY'] != "USDT":
        try:
            df = pd.DataFrame(tmp.position)
            matched_row = df[(df['Contract'] == row['CONTRACT']) & (df['Exchange'] == row['EXCHANGE'])].to_dict(orient='records')[0]['MarkPrice']
            #price = g.current_price(row['SYMBOL'])
            return float(matched_row) * float(row['SIZE'])
        except:
            return 0
    else:
        return float(row['SIZE'])

def gateFunding(api_key, api_secret, exchange):
    try:
        fund = g.send_signed_request('/futures/usdt/account_book', api_key, api_secret)
        #print(f"{fund}\n################################################################\n")
        df = pd.DataFrame(fund)
        df = df[df['type'] == 'fund']
        df['VENUE'] = "Gate"
        df['EXCHANGE'] = exchange
        df['TYPE'] = 'FUNDING_FEE'
        df['SIZE'] = df['change']
        df['TIME'] = df['time'].astype(float) * 1000
        df['CONTRACT'] = df['text']
        df['SYMBOL'] = df.apply(split_text, args=(0, ), axis=1)
        df['CURRENCY'] = df.apply(split_text, args=(1, ), axis=1)
        df['FEE'] = df.apply(gate_price, axis=1)
        df = df[['TIME', 'VENUE', 'SYMBOL', 'TYPE', 'SIZE', 'CURRENCY', 'EXCHANGE', 'CONTRACT', 'FEE']]
        return df
    except:
        return pd.DataFrame()

#gateFunding(keys.gate_key, keys.gate_secret, "GATE")

def convert_epoch(row):
    #if row['VENUE'] == 'Gate':
    #    timeRow = row['TIME']
    #    value = datetime.datetime.fromtimestamp(timeRow)
    #    return value.strftime('%Y-%m-%d %H:%M:%S')
    #else:
    #    timeRow = row['TIME'] / 1000
    #    value = datetime.datetime.fromtimestamp(timeRow)
    #    return value.strftime('%Y-%m-%d %H:%M:%S')
    timeRow = row['TIME'] / 1000
    value = datetime.datetime.fromtimestamp(timeRow)
    #return value.strftime('%Y-%m-%d %H:%M:%S')
    return value.strftime('%Y-%m-%d %H:%M')

def build_csv():

    #results = [None] * 8

    def run_exchange(index, func, *args):
        ###Helper function to store results in index neatly
        results[index] = func(*args)

    print('Starting to build report csv')

    endtime = int(time.time() * 1000)

    #threads = [
    #    threading.Thread(target=run_exchange, args=(0, binanceFunding, False, keys.binance_key, keys.binance_secret, "Binance")),
    #    threading.Thread(target=run_exchange, args=(1, binanceFunding, False, keys.binance_sub1_key, keys.binance_sub1_secret, "Binance_Sub1")),
    #    threading.Thread(target=run_exchange, args=(2, binanceFunding, False, keys.binance_sub2_key, keys.binance_sub2_secret, "Binance_Sub2")),
    #    threading.Thread(target=run_exchange, args=(3, binanceFunding, False, keys.binance_sub3_key, keys.binance_sub3_secret, "Binance_Sub3")),
    #    threading.Thread(target=run_exchange, args=(4, run_bybit, False, keys.bybit_key, keys.bybit_secret, "Bybit", endtime)),
    #    threading.Thread(target=run_exchange, args=(5, gateFunding, keys.gate_key, keys.gate_secret, "Gate")),
    #    threading.Thread(target=run_exchange, args=(6, binanceFunding, False, keys.binance_sub4_key, keys.binance_sub4_secret, "Binance_Sub4")),
    #    threading.Thread(target=run_exchange, args=(7, run_bybit, False, keys.bybit_sub_1_key, keys.bybit_sub_1_secret, "Bybit_sub1", endtime)),
    #

    threads = [
        threading.Thread(target=run_exchange, args=(0, binanceFunding, False, keys.binance_key, keys.binance_secret, "Binance")),
        threading.Thread(target=run_exchange, args=(1, binanceFunding, False, keys.binance_sub1_key, keys.binance_sub1_secret, "Binance_Sub1")),
        threading.Thread(target=run_exchange, args=(2, binanceFunding, False, keys.binance_sub2_key, keys.binance_sub2_secret, "Binance_Sub2")),
        threading.Thread(target=run_exchange, args=(3, binanceFunding, False, keys.binance_sub3_key, keys.binance_sub3_secret, "Binance_Sub3")),
        threading.Thread(target=run_exchange, args=(4, binanceFunding, False, keys.binance_sub4_key, keys.binance_sub4_secret, "Binance_Sub4")),
        threading.Thread(target=run_exchange, args=(5, run_bybit, False, keys.bybit_key, keys.bybit_secret, "Bybit", endtime)),
        threading.Thread(target=run_exchange, args=(6, gateFunding, keys.gate_key, keys.gate_secret, "Gate")),
        #threading.Thread(target=run_exchange, args=(6, run_bybit, False, keys.bybit_sub_1_key, keys.bybit_sub_1_secret, "Bybit_sub1", endtime)),
    ]

    results = [None] * len(threads)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print('Made report calls')

    #concat = pd.concat([b1, by1, by2, g1, b2, b3, b4, b5], axis=0)
    concat = pd.concat(results, axis=0)
    concat = concat.sort_values(by="TIME", ascending=False)
    concat['TIME'] = concat.apply(convert_epoch, axis=1)

    print('Report table built')

    return concat

#print(build_csv())
#end = time.time()
#print(f"Took {end-start} seconds")

def get_rewards():
    #fbr = fb.collectRewards()
    #fbr = fb.final_collection()
    #fbr = fbr.sort_values(by="SYMBOL", ascending=True)
    #fbr['TIME'] = fbr.apply(convert_epoch, axis=1)

    fbr = fb.collect_rewards()
    try:
        fbr = fbr.sort_values(by="SYMBOL", ascending=True)
        fbr['TIME'] = fbr.apply(convert_epoch, axis=1)
    except:
        pass

    return fbr


#try:
#    #get_rewards()a
#    build_csv()
#    print("DONE")
#except Exception as e:
#    print(e)
#build_csv()
