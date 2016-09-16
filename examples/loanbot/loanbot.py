#!/usr/bin python
import time, logging, os, json
from multiprocessing.dummy import Process as Thread
import poloniex

W  = '\033[0m'  # white (normal)
R  = lambda text: '\033[31m'+text+W # red
G  = lambda text: '\033[32m'+text+W # green
O  = lambda text: '\033[33m'+text+W # orange
B  = lambda text: '\033[34m'+text+W # blue
P  = lambda text: '\033[35m'+text+W # purp
C  = lambda text: '\033[36m'+text+W # cyan
GR = lambda text: '\033[37m'+text+W # gray

class Loaner(object):
    """ Object for control of threaded Loaner loop"""
    def __init__(self, config):
        if os.path.isfile(config):
            with open(config) as f:
                config = json.load(f)
        self.polo = poloniex.Poloniex(config['key'], config['secret'])
        self.coins = config['coins']
        self.interval = config['interval']
        self._running, self._thread = False, None
        self.openLoanOffers = None
        self.availBalance = None
        
    def _run(self):
        """
        Main loop that is threaded (set Loaner._running to 'False' to stop loop)
        """
        while self._running:
            try:
                self.openLoanOffers = self.polo.myOpenLoanOrders()
                for coin in self.coins:
                    # Check for old offers
                    self.cancelOldOffers(coin)
                self.availBalance = self.polo.myAvailBalances()
                for coin in self.coins:
                    # ALL the coins??
                    if self.coins[coin]['allBal']:
                        self.moveAll2Lending(coin)
                self.availBalance = self.polo.myAvailBalances()
                for coin in self.coins:
                    # Creat new offer
                    self.createLoanOffer(coin)
                # wait the interval (or shutdown)
                for i in range(self.interval*2):
                    if not self._running:
                        break
                    time.sleep(0.5)
            except Exception as e:
                logging.exception(e)
                time.sleep(10)

    def start(self):
        """ Start Loaner.thread"""
        self._thread = Thread(target=self._run)
        self._thread.daemon = True
        self._running = True
        self._thread.start()
        logging.info(P('LOANER:')+C(' started'))

    def stop(self):
        """ Stop Loaner.thread"""
        self._running = False
        self._thread.join()
        logging.info(P('LOANER:')+R(' stopped'))
    
    def moveAll2Lending(self, coin):
        if 'exchange' in self.availBalance:
            if coin in self.availBalance['exchange']:
                result = self.polo.transferBalance(
                    coin,
                    self.availBalance['exchange'][coin],
                    'exchange',
                    'lending'
                    )
                if 'error' in result:
                    raise RuntimeError(P('LOANER:')+' %s' % R(result['error']))
                else:
                    logging.info(P('LOANER:')+' %s' % result['message'])
        if 'margin' in self.availBalance:
            if coin in self.availBalance['margin']:
                result = self.polo.transferBalance(
                    coin, self.availBalance['margin'][coin], 'margin', 'lending'
                    )
                if 'error' in result:
                    raise RuntimeError(P('LOANER:')+' %s' % R(result['error']))
                else:
                    logging.info(P('LOANER:')+' %s' % result['message'])

    def getLoanOfferAge(self, coin, order):
        # epoch of loan order 
        opnTime = self.poloniex.UTCstr2epoch(order['date'])
        # current epoch
        curTime = time.time()
        # age of open order = now-timeopened
        orderAge = (curTime-opnTime)
        logging.info(P('LOANER:')+' %s order %s has been open %s mins' % (
                C(coin), G(str(order['id'])), C(str(orderAge/60))
                ))
        return orderAge

    def cancelOldOffers(self, coin):
        if coin in self.openLoanOffers:
            for offer in self.openLoanOffers[coin]:
                age = self.getLoanOfferAge(coin, offer)
                # check if it is beyond max age
                if age > self.coins[coin]['maxAge']:
                    result = self.polo.cancelLoanOrder(offer['id'])
                    if 'error' in result:
                        raise RuntimeError(P('LOANER:')+' %s' % R(result['error']))
                    else:
                        logging.info(P('LOANER:')+' %s [ID: %s]' % (
                            C(result['message']), G(str(offer['id']))
                            ))

    def createLoanOffer(self, coin):
        if 'lending' in self.availBalance:
            if coin in self.availBalance['lending']:
                # and amount is more than min
                if float(self.availBalance['lending'][coin]) > self.coins[coin]['minAmount']:
                    # get lowset rate
                    topRate = float(
                            self.polo.marketLoans(coin)['offers'][0]['rate']
                            )
                    # create loan
                    result = self.polo.createLoanOrder(
                            coin,
                            self.availBalance['lending'][coin],
                            topRate+(self.coins[coin]['offset']*0.000001)
                            )
                    if 'error' in result:
                        raise RuntimeError(P('LOANER:')+' %s' % R(result['error']))
                    else:
                        logging.info(P('LOANER:')+' %s %s [Amount: %s Rate: %s]' % (
                                C(coin),
                                result['message'].lower(),
                                O(str(self.availBalance['lending'][coin])),
                                O(str(100*(topRate+(self.coins[coin]['offset']*0.000001)))+'%')
                                ))

if __name__ == "__main__":
    import argparse
    import sys
    logging.basicConfig(
            format='[%(asctime)s]%(message)s',
            datefmt=G("%H:%M:%S"),
            level=logging.INFO
            )
    parser = argparse.ArgumentParser(description='A Simple Poloniex Loanbot!')
    parser.add_argument('config')
    args = parser.parse_args()
    bot = Loaner(args.config)
    bot.start()
    while 1:
        try:
            time.sleep(0.5)
        except:
            bot.stop()
            sys.exit()
