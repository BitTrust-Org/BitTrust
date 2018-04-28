from urllib.request import Request, urlopen
from sqlalchemy import create_engine
import json
import main as m

# Class to add variables to database
class orderBook():
    def __init__(self, type, price, amount, priceByAmount, exchange):
        self.type = type
        self.price = price
        self.amount = amount
        self.priceByAmount = priceByAmount
        self.exchange = exchange

    # perform insertions to the table.
    def addToDB(self, orderBook):
        conn.execute("INSERT INTO orderBooks (type, price, amount, bitcoinCount, exchange) " +
                     "VALUES ('" + str(orderBook.type) + "', " + str(orderBook.price) +
                     ", " + str(orderBook.amount) + ", " + str(orderBook.priceByAmount) + ", '" + str(orderBook.exchange) +"')")

# parse the data returned from api
def data_parse(data):
    data = data[2:-1]
    data = json.loads(data)
    # Store the bids and asks in database
    bidsData = data['bids']
    askData = data['asks']
    # get rid of divide by 0 error
    rangeminMax = m.getMeanAndStDevBitCoinPrice()
    for i in range(0,len(bidsData)):
        # get rid of divide by 0 error
        if float(bidsData[i][1]) > 0:
            priceByAmount = float(bidsData[i][0])/float(bidsData[i][1])
            # check if the ratio is within the allowable acceptable region
            if float(priceByAmount) >= rangeminMax[0] and float(priceByAmount) <= rangeminMax[1]:
                o = orderBook('bid', bidsData[i][0], bidsData[i][1], priceByAmount, "Bitstamp")
                o.addToDB(o)
    for i in range(0,len(askData)):
        # get rid of divide by 0 error
        if float(bidsData[i][1]) > 0:
            priceByAmount = float(bidsData[i][0])/float(bidsData[i][1])
            # check if the ratio is within the allowable acceptable region
            if float(priceByAmount) >= rangeminMax[0] and float(priceByAmount) <= rangeminMax[1]:
                o = orderBook('ask', askData[i][0], askData[i][1], priceByAmount, "Bitstamp")
                o.addToDB(o)

def main():
    # API endpoint
    request = Request('https://www.bitstamp.net/api/v2/order_book/btcusd/')
    # Open URL and start reading
    response = urlopen(request)
    data = response.read()
    data_parse(str(data))
    print("--------bitstamp Data added")


def init():
    print("--------Start Getting Data from bitstamp API")
    global conn
    # Create engine for the Database
    conn = create_engine("sqlite:///mydb.db").connect()
    main()