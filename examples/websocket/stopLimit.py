import poloniex

class StopPoloniex(poloniex.PoloniexSocketed):
    def __init__(self, *args, **kwargs):
        super(StopPoloniex, self).__init__(*args, **kwargs)
        # holds stop orders
        self.stopOrders = {}

    def on_ticker(self, msg):
        data = [float(dat) for dat in msg]
        # check stop orders
        mkt = self.channels[str(data[0])]['name']
        la = data[2]
        hb = data[3]
        for id in self.stopOrders:
            # market matches and the order hasnt triggered yet
            if str(self.stopOrders[id].market) == str(mkt) and not self.stopOrders[id]['order']:
                self.logger.debug('%s lowAsk=%s highBid=%s', mkt, str(la), str(hb))
                self._check_stop(id, la, hb)



    def _check_stop(self, id, lowAsk, highBid):
        amount = self.stopOrders[id]['amount']
        stop = self.stopOrders[id]['stop']
        test = self.stopOrders[id]['test']
        # sell
        if amount < 0 and stop >= float(highBid):
            # dont place order if we are testing
            if test:
                self.stopOrders[id]['order'] = True
            else:
                # sell amount at limit
                self.stopOrders[id]['order'] = self.sell(
                    self.stopOrders[id]['market'],
                    self.stopOrders[id]['limit'],
                    abs(amount))

            self.logger.info('%s sell stop order triggered! (%s)',
                             self.stopOrders[id]['market'],
                             str(stop))
            if self.stopOrders[id]['callback']:
                self.stopOrders[id]['callback'](id)

        # buy
        if amount > 0 and stop <= float(lowAsk):
            # dont place order if we are testing
            if test:
                self.stopOrders[id]['order'] = True
            else:
                # buy amount at limit
                self.stopOrders[id]['order'] = self.buy(
                    self.stopOrders[id]['market'],
                    self.stopOrders[id]['limit'],
                    amount)

            self.logger.info('%s buy stop order triggered! (%s)',
                             self.stopOrders[id]['market'],
                             str(stop))
            if self.stopOrders[id]['callback']:
                self.stopOrders[id]['callback'](id)


    def addStopLimit(self, market, amount, stop, limit, callback=None, test=False):
        self.stopOrders[market+str(stop)] = {'market': market,
                                             'amount': amount,
                                             'stop': stop,
                                             'limit': limit,
                                             'callback': callback,
                                             'test': test,
                                             'order': False
                                            }
        self.logger.debug('%s stop limit set: [Amount]%.8f [Stop]%.8f [Limit]%.8f',
                          market, amount, stop, limit)



if __name__ == '__main__':
    import logging
    logging.basicConfig()
    test = StopPoloniex('key', 'secret')
    def callbk(id):
        print(test.stopOrders[id])
    test.logger.setLevel(logging.DEBUG)
    tick = test.returnTicker()
    test.addStopLimit(market='BTC_LTC',
                      amount=0.5,
                      stop=float(tick['BTC_LTC']['lowestAsk'])+0.000001,
                      limit=float(0.004),
                      callback=callbk
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
