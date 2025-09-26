import requests, sys, time
import pandas as pd

[sys.path.append(directory) for directory in ['config', 'html']]
import keys, tmp, total

#def monitor(data, checkCol, name, token , ID):
#    df = pd.DataFrame(data)
#    sendAlert(f"{name}: {df[checkCol][0]}", token, ID)
#    #rint(f"{name}: {df[checkCol][0]}")

def sendAlert(var, token, chatID):
    #TOKEN = keys.cryptoMonitor_Token
    #chat_id = keys.cryptoMonitor_Id
    TOKEN = token
    chat_id = chatID
    message = var
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json()

#print(total.over, tmp.nextFund[0]['nextFunding'])

try:
    bal = float(total.over)
except:
    bal = total.over
try:
    fund = float(tmp.nextFund[0]['nextFunding'])
except:
    fund = tmp.nextFund[0]['nextFunding']

try:
    balFormat = '{:,.2f}'.format(bal)
except:
    balFormat = bal
try:
    fundFormat = '{:,.2f}'.format(fund)
except:
    fundFormat = fund

sendAlert(f"Current Balance: {balFormat}", keys.cryptoMonitor_Token, keys.cryptoMonitor_Id)
sendAlert(f"Next Funding: {fundFormat}", keys.cryptoMonitor_Token, keys.cryptoMonitor_Id)
print('checks complete sleeping...')
time.sleep(1800)  # Adjust the sleep time for the monitor functions

