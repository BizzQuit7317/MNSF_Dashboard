import requests
import pandas as pd

class BtcNodeAnalytics:
    def __init__(self, address):
        self.address = address
        self.base_url = "https://mempool.space/api"

    def get_account_balance(self):
        endpoint = f"/address/{self.address}"
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url).json()["chain_stats"]
        return (response["funded_txo_sum"]-response["spent_txo_sum"]) / 1e8
