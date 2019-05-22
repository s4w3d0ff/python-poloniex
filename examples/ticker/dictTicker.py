import poloniex

class TickPolo(poloniex.PoloniexSocketed):
    def __init__(self, *args, **kwargs):
        super(TickPolo, self).__init__(*args, **kwargs)
        self.tick = {}
        iniTick = self.returnTicker()
        self._ids = {market: iniTick[market]['id'] for market in iniTick}
        for market in iniTick:
            self.tick[self._ids[market]] = iniTick[market]

    def ticker(self, market=None):
        if market:
            return self.tick[market]
        return self.tick

    def on_ticker(self, data):
        data = [float(dat) for dat in data]
        self.tick[int(data[0])] = {'id': int(data[0]),
                                  'last': data[1],
                                  'lowestAsk': data[2],
                                  'highestBid': data[3],
                                  'percentChange': data[4],
                                  'baseVolume': data[5],
                                  'quoteVolume': data[6],
                                  'isFrozen': data[7],
                                  'high24hr': data[8],
                                  'low24hr': data[9]
                                  }

if __name__ == '__main__':
    polo = TickPolo()
    polo.startws(['ticker'])
    for i in range(6):
        print(polo.ticker('BTC_LTC'))
        poloniex.sleep(2)
    print(polo.ticker())
    polo.stopws()
