import requests, sys, time
import pandas as pd

[sys.path.append(directory) for directory in ['/var/www/html/config', '/var/www/html/html']]
import keys, tmp

def check(data, checkCol, symbol, threshold, nameCol, token , ID):
    df = pd.DataFrame(data)
    leverage_cols = df.filter(like=checkCol).columns
    if symbol == '>':
        condition = (df[leverage_cols].apply(pd.to_numeric, errors='coerce') >= threshold).any(axis=1)
    elif symbol == '<':
        condition = (df[leverage_cols].apply(pd.to_numeric, errors='coerce') <= threshold).any(axis=1)
    else:
        print(f"wowawiewa there was an error!!!! use a real symbol either < or >")
    try:
        value = df[condition][checkCol]
        #print(f"VALUE: {value}")
    except Exception as e:
        #print(f"Error in value calculation!!! {e}")
        value = []
    names = []
    for i in nameCol:
        names.append(df[condition][i])
    if len(value) != 0:
        for i in range(0, len(df)+1):
            try:
                if names[0][i] == 'Hercle' and value[i] >= 10:
                    try:
                        sendAlert(f"{checkCol} alert for {nameCol[0]} {names[0][i]} and {nameCol[1]} {names[1][i]} with {checkCol} of {value[i]}", token , ID)
                    except:
                        pass
                else:
                    try:
                        sendAlert(f"{checkCol} alert for {nameCol[0]} {names[0][i]} and {nameCol[1]} {names[1][i]} with {checkCol} of {value[i]}", token , ID)
                        print(f"{checkCol} alert for {nameCol[0]} {names[0][i]} and {nameCol[1]} {names[1][i]} with {checkCol} of {value[i]}")
                    except:
                        sendAlert(f"{checkCol} alert for {nameCol[0]} {names[0][i]} with {checkCol} of {value[i]}", token , ID)
                        print(f"{checkCol} alert for {nameCol[0]} {names[0][i]} with {checkCol} of {value[i]}")
            except:
                pass

def sendAlert(var, token, chatID):
    #TOKEN = keys.cryptoMonitor_Token
    #chat_id = keys.cryptoMonitor_Id
    TOKEN = token
    chat_id = chatID
    message = var
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json()


check(tmp.leverage, 'Leverage_PUV', '>', 4.5, ['Exchange'], keys.cryptoConnect_Token, keys.cryptoConnect_Id)
check(tmp.position, 'LiqRisk', '<', 0.15, ['Coin', 'Exchange'], keys.cryptoConnect_Token, keys.cryptoConnect_Id)
check(tmp.coinM, 'LiqRisk', '<', 0.15, ['Coin', 'Exchange'], keys.cryptoConnect_Token, keys.cryptoConnect_Id)
check(tmp.leverage, 'Calculation', '<', 15, ['Exchange'], keys.cryptoConnect_Token, keys.cryptoConnect_Id)

try:
    loans = tmp.okx_loan
except:
    loans = [{'Loan Amount': '0', 'Collateral': '0', 'Current LTV': '0', 'Margin Call LTV': '1', 'Liquidation LTV': '1', 'Liquidation Price': '1'}]

if float(loans[0]['Current LTV']) >= float(loans[0]['Margin Call LTV']):
    sendAlert(f"Loan alert for Current LTV: {loans[0]['Current LTV']} over Margin LTV: {loans[0]['Margin Call LTV']}", keys.cryptoConnect_Token, keys.cryptoConnect_Id)
elif float(loans[0]['Current LTV']) >=  float(loans[0]['Margin Call LTV']) - (0.01 * float(loans[0]['Margin Call LTV'])):
    sendAlert(f"Loan alert for Current LTV: {loans[0]['Current LTV']} within 1% of Margin LTV: {loans[0]['Margin Call LTV']}", keys.cryptoConnect_Token, keys.cryptoConnect_Id)


print('Check complete')
#time.sleep(300)  # Adjust the sleep time for the check functions


