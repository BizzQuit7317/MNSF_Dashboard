import hmac, hashlib, time, base64, requests
import pandas as pd
from requests.auth import AuthBase
from concurrent.futures import ThreadPoolExecutor, as_completed

# Create custom authentication class for FalconX Auth
class FXRfqAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
    
    def __call__(self, request):
        timestamp = str(time.time())
        request_body = request.body.decode() if request.body else ''
        message = timestamp + request.method + request.path_url + request_body
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'FX-ACCESS-SIGN': signature_b64,
            'FX-ACCESS-TIMESTAMP': timestamp,
            'FX-ACCESS-KEY': self.api_key,
            'FX-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

class Client():
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = 'https://api.falconx.io/v1/api/native-custody'
        self.account_ids = self.get_account_ids()

    def spot_price(self, COIN):
        try:
            if COIN.lower() == "tau":
                COIN = "tao"
            return requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={COIN.upper()}USDT').json()['price']
        except:
            return 1       

    def send_auth_request(self, ENDPOINT, **kwargs):
        """ Sends an authenticated request and returns JSON response. """
        auth = FXRfqAuth(self.api_key, self.secret_key, self.passphrase)
        try:
            response = requests.get(f"{self.base_url}{ENDPOINT}", auth=auth, **kwargs)
            response.raise_for_status()  # Raise an error for HTTP failures
            return response.json()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
        
    def get_account_ids(self):
        """ Fetches account IDs and returns a list of IDs. """
        r = self.send_auth_request("/accounts")
        if r:
            return [account['id'] for account in r]  # Faster than DataFrame conversion
        return []

    def get_account_assets(self, account_id, EXCHANGE):
        """ Fetches asset balances for a given account. """
        r = self.send_auth_request(f"/balances/account/{account_id}")
        if not r:
            return []
        assets = []
        for j in r.get('networks', []):
            for k in j.get('tokens', []):
                qty = 0
                _id = ""
                
                if float(k.get('custody_balance', 0)) != 0.00:
                    qty = k['custody_balance']
                    _id = "un"
                elif float(k.get('staked_balance', 0)) != 0.00:
                    qty = k['staked_balance']
                    _id = "staking"
                else:
                    continue  # Skip empty balances
                if k['asset'].lower() == "tau":
                    k['asset'] = "tao"
                usd = float(self.spot_price(k['asset'])) * float(qty)
                asset = {
                    "Coin": k['asset'].upper(),
                    "Contract": k['asset'].upper(),
                    "QTY": qty,
                    "USDValue": usd,
                    "Exchange": EXCHANGE,
                    "Account": "SPOT",
                    "id": _id,
                    "reward_to_claim":float(k['rewards_balance'])
                }
                assets.append(asset)
        return assets

    def get_assets(self, EXCHANGE):
        """ Fetches assets for all accounts concurrently. """
        assets = []
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
            future_to_account = {executor.submit(self.get_account_assets, acc_id, EXCHANGE): acc_id for acc_id in self.account_ids}
            
            for future in as_completed(future_to_account):
                try:
                    assets.extend(future.result())
                except Exception as e:
                    print(f"Error processing account {future_to_account[future]}: {e}")
        return pd.DataFrame(assets)

    def get_rewards(self):
        #get assets
        assets = self.get_assets("Falconx")
        #assets = assets[assets['id'] == "staking"]
        #assets['Coin'] = assets['Coin'].replace('tau', 'tao')
        assets['TIME'] = int(time.time()) * 1000 #pd.to_datetime(time.time(), unit='s').strftime('%Y-%m-%d %H:%M')
        assets = assets.rename(columns={'Coin': 'SYMBOL'})
        assets = assets.rename(columns={'Exchange': 'VENUE'})
        assets = assets.rename(columns={'id': 'ID'})
        assets = assets.rename(columns={'reward_to_claim': 'CUMULATIVE'})
        assets['TYPE'] = "REWARD"
        assets['SIZE'] = 0
        assets['EXCHANGE'] = "Falconx"

        """
        keeping track of qty in transfer
        """

        """
        assets = pd.concat([assets, assets], axis=0)
        assets = assets.reset_index(drop=True)
        assets['dupe count'] = assets.groupby(['SYMBOL', 'Contract', 'QTY', 'USDValue', 'VENUE', 'CUMULATIVE', 'TIME', 'TYPE', 'SIZE', 'EXCHANGE']).cumcount()
        assets.loc[assets['dupe count'] == 1, 'ID'] = 'staking_reward'
        assets.loc[assets['ID'] == 'staking_reward', 'CUMULATIVE'] = assets['QTY']
        assets['CUMULATIVE'] = assets['CUMULATIVE'].astype(float)     
        """        

        assets = assets.groupby(['SYMBOL', 'ID']).agg({
            'TIME':'last',
            'VENUE':'last',
            'TYPE':'last',
            'SIZE':'last',
            'EXCHANGE':'last',
            'CUMULATIVE':'sum',
        }).reset_index()
        
        return assets

    def reward_test(self):
        assets = self.get_assets("Falconx")
        assets = assets[(assets['id'] == "staking") | (assets['id'] == "un")]
        assets['id'] = 'staking_test'
        assets['reward_to_claim'] = assets['QTY'].astype(float)

        assets['TIME'] = int(time.time()) * 1000
        assets = assets.rename(columns={'Coin': 'SYMBOL'})
        assets = assets.rename(columns={'id': 'ID'})
        assets = assets.rename(columns={'reward_to_claim': 'CUMULATIVE'})
        assets['TYPE'] = "REWARD"
        assets['SIZE'] = 0
        assets['EXCHANGE'] = "Falconx"
        assets['VENUE'] = "Falconx"
        
        assets = assets.groupby(['SYMBOL', 'ID']).agg({
            'TIME':'last',
            'VENUE':'last',
            'TYPE':'last',
            'SIZE':'last',
            'EXCHANGE':'last',
            'CUMULATIVE':'sum',
        }).reset_index()

        return assets
