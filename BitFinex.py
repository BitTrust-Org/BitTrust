"""Simple Web socket client implementation using Tornado framework.
"""
from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket
import json
from sqlalchemy import create_engine

APPLICATION_JSON = 'application/json'
DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60
relayBitFinex = 1

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

class WebSocketClient():
    """Base for web socket clients.
    """
    def __init__(self, url, connect_timeout=DEFAULT_CONNECT_TIMEOUT, request_timeout=DEFAULT_REQUEST_TIMEOUT):
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.url = url

    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url, connect_timeout=self.connect_timeout, request_timeout=self.request_timeout, headers=headers)
        ws_conn = websocket.WebSocketClientConnection(ioloop.IOLoop.current(), request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')
        self._ws_connection.write_message(escape.utf8(data))

    def close(self):
        """Close connection.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')
        self._ws_connection.close()

    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            if('bitfinex' in self.url):
                self.send('{"event":"subscribe","channel":"book","pair":"BTCUSD","len":1}')
            else:
                self.send('{"type": "subscribe","product_ids": ["BTC-USD"],"channels": ["level2"]}')
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self._on_connection_close()
                break
            self._on_message(msg)

    def _on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """
        global relayBitFinex
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
                o = orderBook(type, relayJsonBitFinex[1][0][0], relayJsonBitFinex[1][0][1], abs(relayJsonBitFinex[1][0][2]), "Bitfinex")
                o.addToDB(o)
            if(relayJsonBitFinex[1][1][1] != 'hb'):
                if (relayJsonBitFinex[1][1][2] >= 0):
                    type = 'bid'
                else:
                    type = 'ask'
                o = orderBook(type, relayJsonBitFinex[1][1][0], relayJsonBitFinex[1][1][1], abs(relayJsonBitFinex[1][1][2]), "Bitfinex")
                o.addToDB(o)
        else:
            relayJsonBitFinex = json.loads(msg)
            if ( relayJsonBitFinex[1] != 'hb'):
                if (relayJsonBitFinex[3] >= 0):
                    type = 'bid'
                else:
                    type = 'ask'
                o = orderBook(type, relayJsonBitFinex[1], relayJsonBitFinex[2], abs(relayJsonBitFinex[3]),"Bitfinex")
                o.addToDB(o)

    def _on_connection_success(self):
        """This is called on successful connection ot the server.
        """
        pass

    def _on_connection_close(self):
        """This is called when server closed the connection.
        """
        pass

    def _on_connection_error(self, exception):
        """This is called in case if connection to the server could
        not established.
        """
        pass

def main():
    bitfinexclient = WebSocketClient('wss://api.bitfinex.com/ws')
    bitfinexclient.connect('wss://api.bitfinex.com/ws')
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        bitfinexclient.close()

def init():
    print("--------Start Relaying Bitfinex")
    global eng
    global conn
    eng = create_engine("sqlite:///mydb.db")
    conn = eng.connect()
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orderBooks'")
    results = str(result.first())
    if('orderBooks' not in results):
        conn.execute("CREATE TABLE orderBooks (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, price REAL, count REAL, amount REAL, exchange TEXT)")
    main()