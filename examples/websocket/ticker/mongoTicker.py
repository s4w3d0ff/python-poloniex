import poloniex
from pymongo import MongoClient  # pip install pymongo

class TickPolo(poloniex.PoloniexSocketed):
    def __init__(self, *args, **kwargs):
        super(TickPolo, self).__init__(*args, **kwargs)
        self.db = MongoClient().poloniex['ticker']
        self.db.drop()
        tick = self.returnTicker()
        for market in tick:
            self.db.update_one(
                {'_id': market}, {'$set': tick[market]}, upsert=True)

    def ticker(self, market=None):
        if market:
            return self.db.find_one({'_id': market})
        return list(self.db.find())

    def on_ticker(self, data):
        data = [float(dat) for dat in data]
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

if __name__ == '__main__':
    polo = TickPolo()
    polo.startws(['ticker'])
    for i in range(6):
        print(polo.ticker('BTC_LTC'))
        poloniex.sleep(2)
    print(polo.ticker())
    polo.stopws()
