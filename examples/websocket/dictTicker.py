import poloniex

class TickPolo(poloniex.Poloniex):
    def __init__(self, *args, **kwargs):
        super(TickPolo, self).__init__(*args, **kwargs)
        # tick holds ticker data
        self.tick = {}
        # get inital ticker data
        iniTick = self.returnTicker()
        # save a dict of the market ids to referace
        self._ids = {market: int(iniTick[market]['id']) for market in iniTick}
        # save ticker data as float instead of str
        for market in iniTick:
            self.tick[self._ids[market]] = {
                item: float(iniTick[market][item]) for item in iniTick[market]
                }


    def ticker(self, market=None):
        '''returns ticker data saved from websocket '''
        if not self._t or not self._running:
            self.logger.error('Websocket is not running!')
            return self.returnTicker()
        if market:
            return self.tick[self._ids[market]]
        return self.tick

    def on_ticker(self, data):
        # save ticker updates to self.tick
        data = [float(dat) for dat in data]
        self.tick[int(data[0])] = {'id': int(data[0]),
                                  'last': data[1],
                                  'lowestAsk': data[2],
                                  'highestBid': data[3],
                                  'percentChange': data[4],
                                  'baseVolume': data[5],
                                  'quoteVolume': data[6],
                                  'isFrozen': int(data[7]),
                                  'high24hr': data[8],
                                  'low24hr': data[9]
                                  }

if __name__ == '__main__':
    from pprint import pprint
    polo = TickPolo()
    poloniex.logging.basicConfig()
    polo.logger.setLevel(poloniex.logging.DEBUG)
    polo.startws(['ticker'])
    for i in range(3):
        pprint(polo.ticker('BTC_LTC'))
        poloniex.sleep(10)
    polo.stopws(3)
