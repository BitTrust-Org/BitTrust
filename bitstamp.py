from urllib.request import Request, urlopen
import json
from sqlalchemy import create_engine

class orderBook():
    def __init__(self, type, price, count, amount, exchange):
        self.type = type
        self.price = price
        self.count = count
        self.amount = amount
        self.exchange = exchange

    def addToDB(self, orderBook):
        conn.execute("INSERT INTO orderBooks (type, price, count, amount, exchange) " +
                     "VALUES ('" + str(orderBook.type) + "', " + str(orderBook.price) +
                     ", " + str(orderBook.count) + ", " + str(orderBook.amount) + ", '" + str(orderBook.exchange) +"')")
        # print('TYPE: {type}. PRICE: {price}. COUNT: {count}. AMOUNT: {amount}. EXCHANGE: {exchange}.'
        #                                             .format(    type=orderBook.type, price=orderBook.price,count=orderBook.count,
        #                                                         amount=orderBook.amount,exchange=orderBook.exchange))
# type, price, amount, count, exchange
def data_parse(data):
    data = data[2:-1]
    data = json.loads(data)
    bidsData = data['bids']
    askData = data['asks']
    for i in range(0,len(bidsData)):
        o = orderBook('bid', bidsData[i][0], 1, bidsData[i][1], "Bitstamp")
        o.addToDB(o)
    for i in range(0,len(askData)):
        o = orderBook('ask', askData[i][0], 1, askData[i][1], "Bitstamp")
        o.addToDB(o)

def main():
    request = Request('https://www.bitstamp.net/api/v2/order_book/btcusd/')
    response = urlopen(request)
    data = response.read()
    data_parse(str(data))
    print("--------bitstamp Data added")


def init():
    print("--------Start Getting Data from bitstamp")
    global eng
    global conn
    eng = create_engine("sqlite:///mydb.db")
    conn = eng.connect()
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orderBooks'")
    results = str(result.first())
    if('orderBooks' not in results):
        conn.execute("CREATE TABLE orderBooks (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, price REAL, amount REAL, count REAL, exchange TEXT)")
    main()