import requests
import pandas as pd

class BtcNodeAnalytics:
    def __init__(self, address):
        self.address = address
        self.base_url = "https://blockchain.info"

    def get_account_balance(self):
        endpoint = f"/rawaddr/{self.address}"
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url)
        return response.json()['final_balance'] / 1e8
