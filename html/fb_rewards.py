import sys, time, pytz, traceback, toml
import pandas as pd
from datetime import datetime
sys.path.append("/var/www/html/config/") # Path to keys file
import keys

sys.path.append("/var/www/html/Exchange_Functions/")
import falconx

sys.path.append("/var/www/html/fb_classes/")
import lpt_node

sys.path.append("/home/ubuntu/control/")
import ssh_class as sc

config = toml.load("/var/www/html/kraken.toml")

def log_kraken(log_data):
    data = f"# config.toml\n"
    for log in log_data:
        data+=f"['{log['SYMBOL']}']\nTime = {log['TIME']}\nSize = {log['SIZE']}\n"
    with open("kraken.toml", "w") as f:
        f.write(f"{data}")

def per_krak(data):
    with open("kraken.log", "a") as f:
        f.write(data)

def get_kraken_rewards(Client):
    sys.path.append("/var/www/html/Exchange_Functions/") # Path to kraken script
    import Kraken

    krakenClient = Kraken.ledgerID(keys.kraken_key, keys.kraken_secret)
    #print(krakenClient)

    df = pd.DataFrame(krakenClient)
    df = df.drop_duplicates(subset='SYMBOL', keep='first')
    log_kraken(df.to_dict(orient='records'))
    current_time = int(round(time.time() * 1000))

    human_readable_time = datetime.fromtimestamp(current_time/1000).strftime('%Y-%m-%d %H:%M:%S')
    per_krak(f"\nrun time: {human_readable_time} request df\n{df}\n")

    try:
        df['SIZE'] = df.apply(krak_size, axis=1)
    except:
        df['SIZE'] = 0

    try:
        df['TIME'] = current_time = int(round(time.time() * 1000))
        df.rename(columns={'Exchange': 'EXCHANGE'}, inplace=True)
        df['CUMULATIVE'] = 0.00


        df['ID'] = "kraken"

        df = df[["TIME", "VENUE", "SYMBOL", "TYPE", "SIZE", "EXCHANGE", "CUMULATIVE", "ID"]]
    except:
        df = pd.DataFrame()
    per_krak(f"\nEnd DF\n{df}\n###########################################################################")
    return df

def manage_krak(update_symbol, new_size):
    rewards = toml.load("/home/ubuntu/control/kraken_latest_rewards.toml") #("/var/www/html/kraken_latest_rewards.toml")
    try:
        update_row = rewards[update_symbol]
        rewards[update_symbol]['Size'] += float(new_size)
    except:
        rewards[update_symbol] = {"Size": float(new_size)}
    #print(rewards)
    with open ("/home/ubuntu/control/kraken_latest_rewards.toml", "w") as f: #("/var/www/html/kraken_latest_rewards.toml", "w") as f:
        f.write("# config.toml\n")
        for i in rewards:
            f.write(f"['{i}']\nSize = {rewards[i]['Size']}\n")

def krak_size(row):
    try:
        config_row = config[row['SYMBOL']]
    except:
        """
        This should only fail for new SYMBOLS, but a new SYMBOL should always be written
        """
        config_row = {"Time":time.time()*1000, "Size":0.00}
        per_krak(f"\n{row['SYMBOL']} was not in kraken.toml!!!")
    try:
        human_run_time = datetime.fromtimestamp(row['TIME']/1000).strftime('%Y-%m-%d %H:%M:%S')
        human_config_time = datetime.fromtimestamp(config_row['Time']/1000).strftime('%Y-%m-%d %H:%M:%S')
        per_krak(f"\n{row['SYMBOL']} time = {human_run_time}, previous time = {human_config_time}, size = {row['SIZE']}")
    except:
        per_krak(f"\n{row['SYMBOL']} time = {row['TIME']}, previous time = {config_row['Time']}, size = {row['SIZE']}")

    try:
        if row['TIME'] == config_row['Time']:
            per_krak(f", data same returned 0")
            return 0 ##No data change from previous so no new data
        else:
            per_krak(f", data changed returned row size")
            manage_krak(row['SYMBOL'], row['SIZE'])
            #print(f"Manage krakc function was run so it shouldve printed")
            return row['SIZE'] ## the data is different so the number must have changed
    except:
        return 1111111

def compute_size(row, result_df):

    try:
        matched_row = result_df[
            (result_df['SYMBOL'] == row['SYMBOL']) &
            (result_df['EXCHANGE'] == row['EXCHANGE']) &
            (result_df['ID'] == row['ID'])
        ]
        if not matched_row.empty:
            try:
                r1 = row['CUMULATIVE'].replace(",","")
            except:
                r1 = row['CUMULATIVE']

            try:
                r2 = matched_row['CUMULATIVE'].values[0].replace(",","")
            except:
                r2 = matched_row['CUMULATIVE'].values[0]


            return float(r1) - float(r2)
        else:
            return 0
    except Exception as e:
        print(f"Error processing row \n{row}: {e}")
        return 0

def get_fireblocks_cum(Client):
    sys.path.append("/var/www/html/fb_classes/")
    import cosmos, harmony, flow

    df_list = []
    current_time = int(round(time.time() * 1000))
    
    try:
        cosmoClientATOM = cosmos.get_cosmos_delegator_balance('')
        entry = {"TIME":current_time, "VENUE":"COSMOS", "SYMBOL":"ATOM", "TYPE":"REWARD", "SIZE":0, "EXCHANGE":"FireBlocks", "CUMULATIVE":cosmoClientATOM["rewards_to_claim"], "ID":"staking"}
        df_list.append(entry)
    except:
        pass

    try:
        cosmoClientATOMCold = cosmos.get_cosmos_delegator_balance('')
        entry = {"TIME":current_time, "VENUE":"COSMOS", "SYMBOL":"ATOM", "TYPE":"REWARD", "SIZE":0, "EXCHANGE":"FireBlocks_Cold", "CUMULATIVE":cosmoClientATOMCold["rewards_to_claim"], "ID":"cold"}
        df_list.append(entry)
    except:
        pass

    try:
        cosmoClientKAVA = cosmos. get_cosmos_delegator_balance('')
        entry = {"TIME":current_time, "VENUE":"COSMOS", "SYMBOL":"KAVA", "TYPE":"REWARD", "SIZE":0, "EXCHANGE":"FireBlocks", "CUMULATIVE":cosmoClientKAVA["rewards_to_claim"], "ID":"un"}
        df_list.append(entry)
    except:
        pass

    try:
        cosmosClientSCRT = cosmos.get_cosmos_delegator_balance('')
        entry = {"TIME":current_time, "VENUE":"COSMOS", "SYMBOL":"SCRT", "TYPE":"REWARD", "SIZE":0, "EXCHANGE":"FireBlocks", "CUMULATIVE":cosmosClientSCRT["rewards_to_claim"], "ID":"un"}
        df_list.append(entry)
    except:
        pass

    try:
        harmClient = harmony.get_harmony_delegator_balance('')
        entry = {"TIME":current_time, "VENUE":"HARMONY", "SYMBOL":"ONE", "TYPE":"REWARD", "SIZE":0, "EXCHANGE":"FireBlocks", "CUMULATIVE":harmClient["rewards_to_claim"], "ID":"un"}
        df_list.append(entry)
    except:
        pass

    try:
        flowClient = flow.get_flow_delegator_balance('')
        entry = {"TIME":current_time, "VENUE":"FLOW", "SYMBOL":"FLOW", "TYPE":"REWARD", "SIZE":0, "EXCHANGE":"FireBlocks", "CUMULATIVE":flowClient["rewards"], "ID":"un"}
        df_list.append(entry)
    except:
        pass
    #try:
    #    falconxClient = falconx.Client(keys.falconx_key, keys.falconx_secret, keys.falconx_pass).get_rewards().to_dict(orient='records')
    #    df_list.extend(falconxClient)
    #except:
    #    pass
    try:
        falconxClient_tes = falconx.Client(keys.falconx_key, keys.falconx_secret, keys.falconx_pass).reward_test().to_dict(orient='records')
        df_list.extend(falconxClient_tes)
    except Exception as e:
        print(f"Error with TAO rewards: {e}")

    try:
        lpt_client = lpt_node.get_lpt_delegator_balance("")['rewards_to_claim']
        df_list.extend()
    except:
        pass


    df = pd.DataFrame(df_list)


    london_tz = pytz.timezone('Europe/London')
    london_time = datetime.now(london_tz)
    formatted_time = london_time.strftime("%H-00")
    formatted_date = london_time.strftime("%Y-%m-%d")

    query = {
            "$or": [
                { "Time": formatted_time, "Date": formatted_date, "SYMBOL": "ATOM", "EXCHANGE": "FireBlocks", "VENUE": "COSMOS" },
                { "Time": formatted_time, "Date": formatted_date, "SYMBOL": "ATOM", "EXCHANGE": "FireBlocks_Cold", "VENUE": "COSMOS" },
                { "Time": formatted_time, "Date": formatted_date, "SYMBOL": "KAVA", "EXCHANGE": "FireBlocks", "VENUE": "COSMOS" },
                { "Time": formatted_time, "Date": formatted_date, "SYMBOL": "SCRT", "EXCHANGE": "FireBlocks", "VENUE": "COSMOS" },
                { "Time": formatted_time, "Date": formatted_date, "SYMBOL": "ONE", "EXCHANGE": "FireBlocks", "VENUE": "HARMONY" },
                { "Time": formatted_time, "Date": formatted_date, "SYMBOL": "FLOW", "EXCHANGE": "FireBlocks", "VENUE": "FLOW" },
                { "Time": formatted_time, "Date": formatted_date, "SYMBOL": "TAO", "EXCHANGE": "Falconx", "VENUE": "Falconx" },
                { "Time": formatted_time, "Date": formatted_date, "SYMBOL": "LPT", "EXCHANGE": "LPT", "VENUE": "LPT" }
            ]
            }

    result = Client.mongo_client.query([query], "rewards")
    df['SIZE'] = df.apply(compute_size, axis=1, result_df=result)

    df = df[["TIME", "VENUE", "SYMBOL", "TYPE", "SIZE", "EXCHANGE", "CUMULATIVE", "ID"]]
    return df

def get_fb_qty(Client):
    sys.path.append("/var/www/html/data/")
    import fireBlocks

    df = pd.DataFrame(fireBlocks.values)

    df = df.drop(df[(df['ID'] == "staking") & (df['Coin'] == "ATOM") & (df['Exchange'] == "FireBlocks")].index)
    df = df.drop(df[(df['ID'] == "cold") & (df['Coin'] == "ATOM") & (df['Exchange'] == "FireBlocks_Cold")].index)
    df = df.drop(df[(df['ID'] == "un") & (df['Coin'] == "KAVA") & (df['Exchange'] == "FireBlocks")].index)
    df = df.drop(df[(df['ID'] == "un") & (df['Coin'] == "SCRT") & (df['Exchange'] == "FireBlocks")].index)
    df = df.drop(df[(df['ID'] == "un") & (df['Coin'] == "ONE") & (df['Exchange'] == "FireBlocks")].index)
    df = df.drop(df[(df['ID'] == "un") & (df['Coin'] == "FLOW") & (df['Exchange'] == "FireBlocks")].index)
    df = df.drop(df[(df['ID'] == "staking") & (df['Coin'] == "TAO") & (df['Exchange'] == "Falconx")].index)


    df = df.rename(columns={'Coin': 'SYMBOL'})
    df = df.rename(columns={"Exchange": 'EXCHANGE'})
    df['TIME'] = int(round(time.time() * 1000)) 
    df['VENUE'] = df.apply(read_dict, axis=1)
    df["TYPE"] = "REWARD"
    df['CUMULATIVE'] = 0.0

    df['SIZE'] = df.apply(compute_size_fb, axis=1, client=Client)

    df = df[["TIME", "VENUE", "SYMBOL", "TYPE", "SIZE", "EXCHANGE", "CUMULATIVE", "ID"]]

    return df

def compute_size_fb(row, client):
    try:
        london_tz = pytz.timezone('Europe/London')
        london_time = datetime.now(london_tz)
        formatted_time = london_time.strftime("%H-00")
        formatted_date = london_time.strftime("%Y-%m-%d")

        row_df_1 = client.mongo_client.query([{"Time":formatted_time}, {"Coin":row['SYMBOL']}, {"Date":formatted_date}, {"ID":row["ID"]}], "fba")


        time_hour = int(formatted_time.split("-")[0])-1

        if time_hour <= 9:
            formatted_time = f"0{int(time_hour)}-00"
        else:
            formatted_time = f"{time_hour}-00"

        row_df_2 = client.mongo_client.query([{"Time":formatted_time}, {"Coin":row['SYMBOL']}, {"Date":formatted_date}, {"ID":row["ID"]}], "fba")

        float_df_1 = row_df_1['QTY'][0].replace(",","")
        float_df_2 = row_df_2['QTY'][0].replace(",","")

        #float(float_df_1) - float(float_df_2)
        #return float(float_df_1) - float(float_df_2)
        size = float(float_df_1) - float(float_df_2)

        if row['SYMBOL'] == 'KSM':
            if size > 20000.00:
                size = 0
            elif size < 0:
                size = 0

        return size
    except:
        return 0

def read_dict(row):
    venues = {'LPT':'LPT', 'BTC':'BTC', 'ATOM':'COSMOS', 'AVAX':'AVAX', 'CTSI':'CARTESI', 'FLOW':'FLOW', 'KAVA':'COSMOS', 'KSM':'KUSAMA', 'NEAR':'NEAR', 'ONE':'HARMONY', 'ROSE':'OASIS', 'SCRT':'COSMOS', 'XTZ':'TEZOS', 'ETH':'ETH', 'ROSE Old':'OASIS'}
    return venues[row['SYMBOL']]

def run_logger(status, kraken_output):
    runTime = time.time()
    readable_date = datetime.fromtimestamp(runTime).strftime('%Y-%m-%d %H:%M:%S')
    with open("/var/www/html/reward.log", "a") as f:
        f.write(f"{status} run at {readable_date}\n{kraken_output}\n#########################################\n")

def collect_rewards():
    try:
        #try:
        #    Client = sc.SSHClient("18.169.147.67", 22, "ubuntu",  "", "/dev/ssh_keys/Mongo_Server.pem")
        #except:
        #    Client = sc.SSHClient("18.169.147.67", 22, "ubuntu",  "", "/home/ubuntu/tran_test/main/Mongo_Server.pem")

        Client = sc.SSHClient("18.169.147.67", 22, "ubuntu",  "", "/home/ubuntu/tran_test/main/Mongo_Server.pem")

        Client.connect()
        Client.open_ssh_tunnel("localhost", 27017, 27018)
        Client.create_mongo_client(27018, "Snapshots")

        fbrc = get_fireblocks_cum(Client)
        k = get_kraken_rewards(Client)
        fba = get_fb_qty(Client)

        df = pd.concat([fbrc, k, fba])

        Client.close_all()
        
        run_logger("Succesfully", k)

        return df
    except Exception as e:
        run_logger("Unsuccesfully", "No output error with Kraken")
        print(f"Main thread Error: {e}")
        traceback.print_exc()

#collect_rewards()
