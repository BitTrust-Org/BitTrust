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
relayGDax= 1
id = 1

class orderBook():
    global id
    def __init__(self, type, price, count, amount, exchange):
        global id
        self.id = id
        self.type = type
        self.price = price
        self.count = count
        self.amount = amount
        self.exchange = exchange
        id += 1


    def addToDB(self, orderBook):
        conn.execute("INSERT INTO orderBooks (type, price, amount, count, exchange, pairname) " +
                     "VALUES ('" + str(orderBook.type) + "', " + str(orderBook.price) +
                     ", " + str(orderBook.amount) + ", " + str(orderBook.count) + ", '" + str(orderBook.exchange) +
                     "', 'BTCUSD')")
        # print('PRIMARY KEY: {id} .TYPE: {type} .PRICE: {price} .COUNT: {count} .AMOUNT: {amount} .EXCHANGE: {exchange} .'
        #      'Pairname: BTCUSD .'.format( id=orderBook.id,type=orderBook.type,
        #                                                                   price=orderBook.price,count=orderBook.count,
        #                                                                 amount=orderBook.amount,exchange=orderBook.exchange))
        pass
class WebSocketClient():

    """Base for web socket clients.
    """

    def __init__(self, url, connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

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
        if ('bitfinex' in self.url):
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
                    o = orderBook(type, relayJsonBitFinex[1][0][0], relayJsonBitFinex[1][0][1], relayJsonBitFinex[1][0][2],
                                  "Bitfinex")
                    o.addToDB(o)
                if(relayJsonBitFinex[1][1][1] != 'hb'):
                    if (relayJsonBitFinex[1][1][2] >= 0):
                        type = 'bid'
                    else:
                        type = 'ask'
                    o = orderBook(type, relayJsonBitFinex[1][1][0], relayJsonBitFinex[1][1][1], relayJsonBitFinex[1][1][2],
                                  "Bitfinex")
                    o.addToDB(o)
            else:
                relayJsonBitFinex = json.loads(msg)
                if ( relayJsonBitFinex[1] != 'hb'):
                    if (relayJsonBitFinex[3] >= 0):
                        type = 'bid'
                    else:
                        type = 'ask'
                    o = orderBook(type, relayJsonBitFinex[1], relayJsonBitFinex[2], relayJsonBitFinex[3],"Bitfinex")
                    o.addToDB(o)
        else:
            global relayGDax
            if(relayGDax==1):
                relayGDax+=1
                snapshotGdax = json.loads(msg)
                for i in range(0, len(snapshotGdax['bids'])):
                    o = orderBook('bid', snapshotGdax['bids'][i][0], snapshotGdax['bids'][i][1], '1', "GDax")
                    o.addToDB(o)
                for i in range(0, len(snapshotGdax['asks'])):
                    o = orderBook('ask', snapshotGdax['asks'][i][0], snapshotGdax['asks'][i][1], '1', "GDax")
                    o.addToDB(o)
            elif(relayGDax==2):
                relayGDax += 1
            else:
                snapshotGdax = json.loads(msg)
                if(float(snapshotGdax['changes'][0][2]) > 0):
                    if (snapshotGdax['changes'][0][0] == 'buy'):
                        type = 'bid'
                    else:
                        type = 'ask'
                    o = orderBook(type, snapshotGdax['changes'][0][1], snapshotGdax['changes'][0][2], '1', "GDax")
                    o.addToDB(o)
        pass

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
    gdaxclient = WebSocketClient('wss://ws-feed.gdax.com')
    gdaxclient.connect('wss://ws-feed.gdax.com')
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        bitfinexclient.close()
        gdaxclient.close()


def init():
    print("--------Start Relaying information through WebSocket Connection to Bitfinex and GDax")
    global eng
    global conn
    eng = create_engine("sqlite:///mydb.db")
    conn = eng.connect()
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orderBooks'")
    results = str(result.first())
    if('orderBooks' not in results):
        conn.execute("CREATE TABLE orderBooks (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, price REAL, amount REAL, count REAL, exchange TEXT, pairname TEXT)")
    main()