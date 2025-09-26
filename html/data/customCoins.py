import requests, sys, toml
sys.path.append("/home/ubuntu/tran_test/classes")
import mongo_class, ssh_class
sys.path.append("/var/www/html/config")
import keys
sys.path.append("/var/www/html/Exchange_Functions")
import falconx

config_data = toml.load("/home/ubuntu/db_adjust/config/config.toml")
ssh_details = config_data['ssh']
mongo_details = config_data['mongo']
log_path = config_data['log']['path']

Client = ssh_class.SSHClient(ssh_details['ip'], ssh_details['port'], ssh_details['username'],  ssh_details['password'], ssh_details['key_path'])
Client.connect()

Client.open_ssh_tunnel(ssh_details['tunnel_host'], ssh_details['tunnel_port'], ssh_details['port_forward'])
Client.create_mongo_client(ssh_details['port_forward'], "Snapshots")

query = Client.mongo_client.query_direct({"Key":"current"}, "customCoins").to_dict(orient='records')[0]

Credinvest = {'Coin':'USD','Contract':'USD','QTY':round(float(query['FundBank']),6),'USDValue':round(0, 2),'Exchange':'Banks','Account':'SPOT'} #G might call this Fund Bank

ETH = {'Coin':'ETH','Contract':'ETH','QTY':round(float(query['ETH']),6),'USDValue':round(0, 2),'Exchange':'Adj','Account':'EARN'}
USD = {'Coin':'USD','Contract':'USD','QTY':round(float(query['USD']),6),'USDValue':round(0, 2),'Exchange':'Adj','Account':'EARN'}
BTC = {'Coin':'BTC','Contract':'BTC','QTY':round(float(query['BTC']),6),'USDValue':round(0, 2),'Exchange':'Adj','Account':'EARN'}
GAV = query['GAV']
NAV = query['NAV']
BTC_gav = query['BTC_gav']
ETH_gav = query['ETH_gav']
BTCpx_gav = query['BTCpx_gav']
ETHpx_gav = query['ETHpx_gav']
monthly_cost = query['monthlyCost']

option = {'Coin':'USD','Contract':'USD','QTY':round(float(query['Option']),6),'USDValue':round(0, 2),'Exchange':'Option','Account':'SPOT'} #query['Option']
note = {'Coin':'USD','Contract':'USD','QTY':round(float(query['Note']),6),'USDValue':round(0, 2),'Exchange':'Note','Account':'SPOT'} #query['Note']

invoice = {'Coin':'USDC','Contract':'USDC','QTY':round(float(query['Invoice']),6),'USDValue':round(0, 2),'Exchange':'Invoice','Account':'EARN'}

"""
Data under here is on the fly assets not repeating ones
"""
#LP = {'Coin':'LPT','Contract':'LPT','QTY':71023 ,'USDValue':round(0, 2),'Exchange':'FireBlocks','Account':'SPOT'}
