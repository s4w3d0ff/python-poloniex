#!/usr/bin/python
# -*- coding: utf-8 -*-
import websocket  # pip install websocket-client
from pymongo import MongoClient  # pip install pymongo

from poloniex import Poloniex

from multiprocessing.dummy import Process as Thread
import json
import logging

logger = logging.getLogger(__name__)


class wsTicker(object):

    def __init__(self, api=None):
        self.api = api
        if not self.api:
            self.api = Poloniex(jsonNums=float)
        self.db = MongoClient().poloniex['ticker']
        self.db.drop()
        self.ws = websocket.WebSocketApp("wss://api2.poloniex.com/",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open

    def __call__(self, market=None):
        """ returns ticker from mongodb """
        if market:
            return self.db.find_one({'_id': market})
        return list(self.db.find())

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'error' in message:
            print(message['error'])
            return

        if message[0] == 1002:
            if message[1] == 1:
                print('Subscribed to ticker')
                return

            if message[1] == 0:
                print('Unsubscribed to ticker')
                return

            data = message[2]

            self.db.update_one(
                {"id": float(data[0])},
                {"$set": {'last': data[1],
                          'lowestAsk': data[2],
                          'highestBid': data[3],
                          'percentChange': data[4],
                          'baseVolume': data[5],
                          'quoteVolume': data[6],
                          'isFrozen': data[7],
                          'high24hr': data[8],
                          'low24hr': data[9]
                          }},
                upsert=True)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("Websocket closed!")

    def on_open(self, ws):
        tick = self.api.returnTicker()
        for market in tick:
            self.db.update_one(
                {'_id': market},
                {'$set': tick[market]},
                upsert=True)
        print('Populated markets database with ticker data')
        self.ws.send(json.dumps({'command': 'subscribe',
                                 'channel': 1002}))

    def start(self):
        self.t = Thread(target=self.ws.run_forever)
        self.t.daemon = True
        self.t.start()
        print('Thread started')

    def stop(self):
        self.ws.close()
        self.t.join()
        print('Thread joined')


if __name__ == "__main__":
    import pprint
    from time import sleep
    # websocket.enableTrace(True)
    ticker = wsTicker()
    ticker.start()
    for i in range(5):
        sleep(10)
        pprint.pprint(ticker('USDT_BTC'))
    ticker.stop()
