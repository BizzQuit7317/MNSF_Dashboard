import sys
import pandas as pd

[sys.path.append(directory) for directory in ['../Exchange_Functions', '../config', '../data', '..']]
import Binance as b
import keys

symbolList = [] #['DOT'] #, 'ONE']
qtyDict = {'DOT':-46921} #, 'ONE':-26978350}
liqPriceDict = {'MINA':0.5049, 'ROSE':0.05384, 'CTSI':0.16456, 'ONE':0, 'DOT':5.8692}
assets = []

def get():
    for i in symbolList:
        try:
           pos = b.binance_send_signed_request("https://fapi.binance.com", 'GET', '/fapi/v2/positionRisk', keys.binance_key, keys.binance_secret, payload={'symbol':i+'USDT'})
        except:
           pos = [{'leverage':0, 'markPrice':0, 'liquidationPrice':0}]
        try:
           price = float(b.coinPrice(i))
           price = (float(price)*qtyDict[i])
        except:
           price = 0
        try:
           risk = (float(pos[0]['liquidationPrice'])-float(pos[0]['markPrice']))/float(pos[0]['markPrice'])
        except:
           risk = 0
        try:
           if i == "ONE":
               asset = {'Coin':i,'Contract':f"{i}USDT",'QTY':qtyDict[i],'USDValue':price,'Exchange':'None','Account':'Earn','Leverage':pos[0]['leverage'],'MarkPrice':pos[0]['markPrice'],'LiqPrice':pos[0]['liquidationPrice'],'LiqRisk':1}
               assets.append(asset)
           elif i == 'DOT':
               asset = {'Coin':i,'Contract':f"{i}_USDT",'QTY':qtyDict[i],'USDValue':price,'Exchange':'Hercle','Account':'Earn','Leverage':pos[0]['leverage'],'MarkPrice':pos[0]['markPrice'],'LiqPrice':pos[0]['liquidationPrice'],'LiqRisk':abs(risk)}
               assets.append(asset)
           else:
               asset = {'Coin':i,'Contract':f"{i}USDT",'QTY':qtyDict[i],'USDValue':price,'Exchange':'Hercle','Account':'Earn','Leverage':pos[0]['leverage'],'MarkPrice':pos[0]['markPrice'],'LiqPrice':pos[0]['liquidationPrice'],'LiqRisk':abs(risk)}
               assets.append(asset)
        except Exception as e:
           print(f"slimey: {e}")

    return (pd.DataFrame(assets))
