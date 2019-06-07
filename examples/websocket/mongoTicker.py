import poloniex
from pymongo import MongoClient  # pip install pymongo

class TickPolo(poloniex.PoloniexSocketed):
    def __init__(self, *args, **kwargs):
        super(TickPolo, self).__init__(*args, **kwargs)
        self.db = MongoClient().poloniex['ticker']
        self.db.drop()
        tick = self.returnTicker()
        self._ids = {market: int(tick[market]['id']) for market in tick}
        for market in tick:
            self.db.update_one(
                {'_id': market},
                {'$set':
                    {item: float(tick[market][item]) for item in tick[market]}
                },
                upsert=True)

    def ticker(self, market=None):
        '''returns ticker data saved from websocket '''
        if not self._t or not self._running:
            self.logger.error('Websocket is not running!')
            return self.returnTicker()
        if market:
            return self.db.find_one({'_id': market})
        return list(self.db.find())

    def on_ticker(self, data):
        data = [float(dat) for dat in data]
        self.db.update_one(
            {"id": int(data[0])},
            {"$set": {'last': data[1],
                    'lowestAsk': data[2],
                    'highestBid': data[3],
                    'percentChange': data[4],
                    'baseVolume': data[5],
                    'quoteVolume': data[6],
                    'isFrozen': int(data[7]),
                    'high24hr': data[8],
                    'low24hr': data[9]
                    }},
            upsert=True)

if __name__ == '__main__':
    polo = TickPolo()
    polo.startws(['ticker'])
    for i in range(3):
        print(polo.ticker('BTC_LTC'))
        poloniex.sleep(10)
    print(polo.ticker())
    polo.stopws(3)
