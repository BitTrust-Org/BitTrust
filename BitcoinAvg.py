import json
from datetime import timedelta
from urllib.request import Request, urlopen
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

id = 1


class BitcoinAvg():
    global id

    def __init__(self, average, date):
        global id
        self.id = id
        self.average = average
        self.date = date
        id += 1

    def addToDB(self, bitcoinAverage):
        conn.execute("INSERT INTO bitcoinAvg (average, time) VALUES (" + str(bitcoinAverage.average) + ", '" + str(
            bitcoinAverage.date) + "')")
        pass


def data_parse(data):
    data = data[2:-1]
    a = data.split("\\n")
    data_input = ""
    for i in range(len(a)):
        data_input += a[i].strip()
    db_input = json.loads(data_input)
    for i in range(0, len(db_input)):
        c = BitcoinAvg(db_input[i]["average"], db_input[i]["time"])
        c.addToDB(c)


def main():
    request = Request('https://apiv2.bitcoinaverage.com/indices/global/history/BTCUSD?period=daily&format=json')
    response = urlopen(request)
    data = response.read()
    print(data)
    data_parse(str(data))
    predict()


def predict():
    results = conn.execute("SELECT average, time from bitcoinAvg")
    average = []
    time = []
    for rows in results:
        data = str(rows).split(", ")
        average.append(float(data[0][1:].strip()))
        time_string = str(data[1])[1:-2] + ".000000"
        time.append(pd.to_datetime(time_string) - timedelta(hours=4))
    plt.plot(time, average)
    plt.gcf().autofmt_xdate()
    plt.show()
    mean_total = sum(average) / len(average)
    mean_half = sum(average[1:(int(len(average) / 2))]) / (len(average) / 2)
    if mean_total >= mean_half:
        print("BUY")
    else:
        print("SELL")


if __name__ == '__main__':
    global eng
    global conn
    eng = create_engine("sqlite:///mydb.db")
    conn = eng.connect()
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bitcoinAvg'")
    results = str(result.first())
    if 'bitcoinAvg' not in results:
        conn.execute("CREATE TABLE bitcoinAvg (id INTEGER PRIMARY KEY AUTOINCREMENT, average REAL, time TEXT)")
    else:
        conn.execute("DROP TABLE bitcoinAvg")
        conn.execute("CREATE TABLE bitcoinAvg (id INTEGER PRIMARY KEY AUTOINCREMENT, average REAL, time TEXT)")
    main()

