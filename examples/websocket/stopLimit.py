import poloniex

class StopLimit(object):
    def __init__(self, market, amount, stop, limit, test=False):
        self.market = str(market)
        self.amount = float(amount)
        self.stop = float(stop)
        self.limit = float(limit)
        self.order = False
        self.logger = poloniex.logging.getLogger('StopLimit')
        self.logger.setLevel(poloniex.logging.DEBUG)
        self.test = test

    def check(self, lowAsk, highBid):
        # sell
        if self.amount < 0 and self.stop >= float(highBid):
            # dont place order if we are testing
            if self.test:
                self.order = True
            else:
                # sell amount at limit
                self.order = self.sell(self.market,
                                       self.limit,
                                       abs(self.amount))

            self.logger.info('%s sell stop order triggered! (%s)',
                             self.market, str(self.stop))
        # buy
        if self.amount > 0 and self.stop <= float(lowAsk):
            # dont place order if we are testing
            if self.test:
                self.order = True
            else:
                # buy amount at limit
                self.order = self.buy(self.market, self.limit, self.amount)

            self.logger.info('%s buy stop order triggered! (%s)',
                             self.market, str(self.stop))

    def __call__(self):
        return self.order


class CPolo(poloniex.PoloniexSocketed):
    def __init__(self, *args, **kwargs):
        super(CPolo, self).__init__(*args, **kwargs)
        self.stopOrders = {}

    def on_ticker(self, msg):
        self._checkStops(msg)

    def _checkStops(self, msg):
        mktid = str(msg[0])
        mkt = self.channels[mktid]['name']
        la = msg[2]
        hb = msg[3]
        for order in self.stopOrders:
            if str(self.stopOrders[order].market) == str(mkt) and not self.stopOrders[order]():
                self.logger.debug('%s lowAsk=%s highBid=%s',
                                  mkt, str(la), str(hb))
                self.stopOrders[order].check(la, hb)

    def addStopLimit(self, market, amount, stop, limit, test=False):
        self.logger.debug('%s stop limit set: [Amount]%.8f [Stop]%.8f [Limit]%.8f',
                          market, amount, stop, limit)
        self.stopOrders[market+str(stop)] = StopLimit(market, amount, stop, limit, test)


if __name__ == '__main__':
    import logging
    logging.basicConfig()
    test = CPolo('key', 'secret')
    test.logger.setLevel(logging.DEBUG)
    tick = test.returnTicker()
    test.addStopLimit(market='BTC_LTC',
                      amount=0.5,
                      stop=float(tick['BTC_LTC']['lowestAsk'])+0.000001,
                      limit=float(0.004),
                      # remove or set 'test' to false to place real orders
                      test=True)

    test.addStopLimit(market='BTC_LTC',
                      amount=-0.5,
                      stop=float(tick['BTC_LTC']['highestBid'])-0.000001,
                      limit=float(0.004),
                      # remove or set 'test' to false to place real orders
                      test=True)
    test.startws(['ticker'])
    poloniex.sleep(120)
    test.stopws(3)
