# dumbticker.py requires pymongo (and pandas)
# it saves the data returned from Poloniex.returnTicker() 
# in a mongodb collection at a set interval within a thread.
from pymongo import MongoClient

from multiprocessing.dummy import Process as Thread
from time import sleep
import logging
logger = logging.getLogger(__name__)


class Ticker(object):

    def __init__(self, api, interval=1):
        self.api = api
        self.db = MongoClient().poloniex['ticker']
        self.interval = interval

    def updateTicker(self):
        tick = self.api.returnTicker()
        for market in tick:
            self.db.update_one({'_id': market},
                               {'$set': tick[market]},
                               upsert=True)
        logger.info('Ticker updated')

    def __call__(self):
        return list(self.db.find())

    def run(self):
        self._running = True
        while self._running:
            self.updateTicker()
            sleep(self.interval)

    def start(self):
        self._thread = Thread(target=self.run)
        self._thread.daemon = True
        self._thread.start()
        logger.info('Ticker started')

    def stop(self):
        self._running = False
        self._thread.join()
        logger.info('Ticker stopped')


if __name__ == '__main__':
    from poloniex import Poloniex
    from pandas import DataFrame
    logging.basicConfig(level=logging.INFO)
    t = Ticker(Poloniex(jsonNums=float))
    t.start()
    sleep(4)
    while t._running:
        try:
            print(DataFrame(t()).set_index('_id')['last']['USDT_BTC'])
            sleep(4)
        except:
            t.stop()
