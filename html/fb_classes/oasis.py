import requests

def get_oasis_wallet_total_balance(address):
    base_url = 'http://api.oasisscan.com/mainnet'
    #base_url = 'http://oasismonitor.com'
    endpoint = '/chain/account/info/{}'.format(address)
    url = base_url + endpoint
    response = requests.get(url)
    bal = float(response.json()['data']['total'])
    return bal