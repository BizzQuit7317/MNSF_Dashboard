import requests, sys, toml
sys.path.append("/home/ubuntu/tran_test/classes")
import mongo_class, ssh_class

config_data = toml.load("/home/ubuntu/db_adjust/config/config.toml")
ssh_details = config_data['ssh']
mongo_details = config_data['mongo']
log_path = config_data['log']['path']

Client = ssh_class.SSHClient(ssh_details['ip'], ssh_details['port'], ssh_details['username'],  ssh_details['password'], ssh_details['key_path'])
Client.connect()

Client.open_ssh_tunnel(ssh_details['tunnel_host'], ssh_details['tunnel_port'], ssh_details['port_forward'])
Client.create_mongo_client(ssh_details['port_forward'], "Snapshots")

query = Client.mongo_client.query_direct({"Key":"current"}, "customCoins").to_dict(orient='records')[0]

XTZ = {'Coin':'XTZ','Contract':'TEZOS','QTY':round(query['XTZ'],6),'USDValue':round(0, 2),'Exchange':'FireBlocks','Account':'SPOT', 'ID':'staking_2'}

