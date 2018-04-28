from urllib.request import Request, urlopen
from sqlalchemy import create_engine
import json

# Class to add variables to database
class BitcoinAverage():
    def __init__(self, average, date):
        self.average = average
        self.date = date

    # perform insertions to the table.
    def addToDB(self, bitcoinAverage):
        conn.execute("INSERT INTO bitcoinAvg (average, time) VALUES (" + str(bitcoinAverage.average) + ", '" + str(
            bitcoinAverage.date) + "')")

# get the data and parse it
def data_parse(data):
    data = data[2:-1]
    a = data.split("\\n")
    data_input = ""
    for i in range(len(a)):
        data_input += a[i].strip()
    db_input = json.loads(data_input)
    for i in range(0, len(db_input)):
        c = BitcoinAverage(db_input[i]["average"],db_input[i]["time"])
        c.addToDB(c)


def main():
    # Start API request to bitcoinaverage.com
    request = Request('https://apiv2.bitcoinaverage.com/indices/global/history/BTCUSD?period=daily&format=json')
    response = urlopen(request)
    data = response.read()
    # Parse the data
    data_parse(str(data))
    print("--------Bitcoin Prices are stored in database")

def init():
    print("--------Start bitcoinaverage API")
    global conn
    # Create the engine and connect to it
    conn = create_engine("sqlite:///mydb.db").connect()
    main()