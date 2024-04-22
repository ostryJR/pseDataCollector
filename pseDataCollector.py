import requests
import json
import mysql.connector
import time as t

import signal

import dbconnect as dbc

url = 'https://www.pse.pl/transmissionMapService'
print("[App]PSE Data Collector Started")

working = True

def dbconn():
    try:
        mydb = mysql.connector.connect(
            host=dbc.host,
            port=dbc.port,
            user=dbc.user,
            password=dbc.password
        )
        return mydb
    except mysql.connector.Error as err:
        print(err)
def signal_handler(sig, _frame):# stopping execution
    print(f'[App]Received signal {sig} - all actions will be stopped')
    global working
    working = False

if dbconn():
    print("[App]Connected to DataBase")

while working:
    signal.signal(signal.SIGTERM, signal_handler)
    mydb = dbconn()

    resp = requests.get(url=url).json()
    #print(resp)

    respDump = json.dumps(resp)
    data = json.loads(respDump)

    status = data['status']
    timestamp = data['timestamp']
    unit = "MW"

    gene = data['data']['podsumowanie']
    heatPower = gene['cieplne']#like coal, gas, NOT heat from earth
    water = gene['wodne']
    wind = gene['wiatrowe']
    solar = gene['PV']
    other = gene['inne']

    production = gene['generacja']
    consumption = gene['zapotrzebowanie']
    frequency = gene['czestotliwosc']

    transfer = data['data']['przesyly']
    SE = [transfer[0]['wartosc'], transfer[0]['rownolegly'], transfer[0]['wartosc_plan']]
    DE = [transfer[1]['wartosc'], transfer[1]['rownolegly'], transfer[1]['wartosc_plan']]
    CZ = [transfer[2]['wartosc'], transfer[2]['rownolegly'], transfer[2]['wartosc_plan']]
    SK = [transfer[3]['wartosc'], transfer[3]['rownolegly'], transfer[3]['wartosc_plan']]
    UA = [transfer[4]['wartosc'], transfer[4]['rownolegly'], transfer[4]['wartosc_plan']]
    LT = [transfer[5]['wartosc'], transfer[5]['rownolegly'], transfer[5]['wartosc_plan']]

    dbcursor = mydb.cursor()

    sql = f'INSERT INTO PSEdata.data(`status`, `timestamp`, `unit`, `cieplne`, `wodne`, `wiatrowe`, `pv`, `inne`, `generacja`, `zapotrzebowanie`, `czestotliwosc`, `SEact`, `SEplan`, `SEparallel`, `DEact`, `DEplan`, `DEparallel`, `CZact`, `CZplan`, `CZparallel`, `SKact`, `SKplan`, `SKparallel`, `UAact`, `UAplan`, `UAparallel`, `LTact`, `LTplan`, `LTparallel`) VALUES ({status},{timestamp},"{unit}",{heatPower},{water},{wind},{solar},{other},{production},{consumption},{frequency}, {SE[0]}, {SE[2]}, {SE[1]}, {DE[0]}, {DE[2]}, {DE[1]}, {CZ[0]}, {CZ[2]}, {CZ[1]}, {SK[0]}, {SK[2]}, {SK[1]}, {UA[0]}, {UA[2]}, {UA[1]}, {LT[0]}, {LT[2]}, {LT[1]});'
    #print(sql)
    dbcursor.execute(sql)
    mydb.commit()
    print(f'[App][{t.ctime()}] TS:', timestamp,". new record inserted.")

    dbcursor.close()
    t.sleep(10)

print(f'[App]App stopped')