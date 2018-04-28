"""Web socket client using Tornado framework.
Please make sure that you are using tornado 4.5.3
"""
from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket
from sqlalchemy import create_engine
import json
import main as m

APPLICATION_JSON = 'application/json'
DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60
relayBitFinex = 1

# This class handles orderbook details to Database
class orderBook():
    # Use the constructor to intialize
    def __init__(self, type, price, amount, priceByAmount, exchange):
        self.type = type
        self.price = price
        self.amount = amount
        self.priceByAmount = priceByAmount
        self.exchange = exchange

    # Perform adding to database.
    def addToDB(self, orderBook):
        # Execute the query to add a row to database
        conn.execute("INSERT INTO orderBooks (type, price, amount, bitcoinCount, exchange) " +
                     "VALUES ('" + str(orderBook.type) + "', " + str(orderBook.price) +
                     ", " + str(orderBook.amount) + ", " + str(orderBook.priceByAmount) + ", '" + str(orderBook.exchange) +"')")

class WebSocketClient():
    # Base for web socket clients.
    def __init__(self, url, connect_timeout=DEFAULT_CONNECT_TIMEOUT, request_timeout=DEFAULT_REQUEST_TIMEOUT):
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.url = url

    # Connect to the server.
    def connect(self, url):
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url, connect_timeout=self.connect_timeout, request_timeout=self.request_timeout, headers=headers)
        ws_conn = websocket.WebSocketClientConnection(ioloop.IOLoop.current(), request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    # Send message to Bitfinex.
    def send(self, data):
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')
        self._ws_connection.write_message(escape.utf8(data))

    # Close the connection.
    def close(self):
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')
        self._ws_connection.close()

    # Once the connection is established.
    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            # send initialization message to bitfinex, indicating currency for orderbooks and initial message
            self.send('{"event":"subscribe","channel":"book","pair":"BTCUSD","len":1}')
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    # Start reading message using Coroutine.
    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self._on_connection_close()
                break
            self._on_message(msg)

    def _on_message(self, msg):
        # This is called when new message is available from the server.
        # Check if the message is the first, second or any other number of reply.
        # First and Second message can be ignored, rest everything is parsed and stored in the DB.
        global relayBitFinex
        # get the range of allowable values from main.py
        rangeminMax = m.getMeanAndStDevBitCoinPrice()
        if(relayBitFinex<=2):
            relayBitFinex += 1
        elif(relayBitFinex==3):
            relayBitFinex += 1
            relayJsonBitFinex = json.loads(msg)
            if(relayJsonBitFinex[1][0][1] != 'hb'):
                if(relayJsonBitFinex[1][0][2]>=0):
                    type = 'bid'
                else:
                    type = 'ask'
                # get rid of divide by 0 error
                if float(relayJsonBitFinex[1][0][1]) > 0:
                    priceByAmount = float(relayJsonBitFinex[1][0][0]) / float(relayJsonBitFinex[1][0][1])
                    # check if the ratio is within the allowable acceptable region
                    if float(priceByAmount) >= rangeminMax[0] and float(priceByAmount) <= rangeminMax[1]:
                        o = orderBook(type, relayJsonBitFinex[1][0][0], relayJsonBitFinex[1][0][1], abs(priceByAmount), "Bitfinex")
                        o.addToDB(o)
            if(relayJsonBitFinex[1][1][1] != 'hb'):
                if (relayJsonBitFinex[1][1][2] >= 0):
                    type = 'bid'
                else:
                    type = 'ask'
                # get rid of divide by 0 error
                if float(relayJsonBitFinex[1][1][1]) > 0:
                    priceByAmount = float(relayJsonBitFinex[1][1][0]) / float(relayJsonBitFinex[1][1][1])
                    # check if the ratio is within the allowable acceptable region
                    if float(priceByAmount) >= rangeminMax[0] and float(priceByAmount) <= rangeminMax[1]:
                        o = orderBook(type, relayJsonBitFinex[1][1][0], relayJsonBitFinex[1][1][1], abs(priceByAmount), "Bitfinex")
                        o.addToDB(o)
        else:
            relayJsonBitFinex = json.loads(msg)
            if ( relayJsonBitFinex[1] != 'hb'):
                if (relayJsonBitFinex[3] >= 0):
                    type = 'bid'
                else:
                    type = 'ask'
                # get rid of divide by 0 error
                if float(relayJsonBitFinex[2]) >0:
                    priceByAmount = float(relayJsonBitFinex[1]) / float(relayJsonBitFinex[2])
                    # check if the ratio is within the allowable acceptable region
                    if float(priceByAmount) >= rangeminMax[0] and float(priceByAmount) <= rangeminMax[1]:
                        o = orderBook(type, relayJsonBitFinex[1], relayJsonBitFinex[2], abs(priceByAmount),"Bitfinex")
                        o.addToDB(o)

    def _on_connection_success(self):
        """This is called on successful connection ot the server.
        """
        pass

def main():
    # Create a websocket object with bitfinex websoclet end point.
    bitfinexclient = WebSocketClient('wss://api.bitfinex.com/ws')
    bitfinexclient.connect('wss://api.bitfinex.com/ws')
    try:
        # Start the thread to relay the information
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        bitfinexclient.close()

def init():
    print("--------Start Relaying Bitfinex")
    global conn
    # Create engine for the Database
    conn = create_engine("sqlite:///mydb.db").connect()
    main()