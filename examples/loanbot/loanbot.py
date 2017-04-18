#!/usr/bin/python
import logging
from time import time, sleep, strptime
from calendar import timegm
from multiprocessing.dummy import Process
from poloniex import Poloniex

logger = logging.getLogger(__name__)

WT = '\033[0m'  # white (normal)
RD = lambda text: '\033[31m' + text + WT  # red
GR = lambda text: '\033[32m' + text + WT  # green
OR = lambda text: '\033[33m' + text + WT  # orange
BL = lambda text: '\033[34m' + text + WT  # blue
PR = lambda text: '\033[35m' + text + WT  # purp
CY = lambda text: '\033[36m' + text + WT  # cyan
GY = lambda text: '\033[37m' + text + WT  # gray

loantoshi = 0.000001


def autoRenewAll(api, toggle=True):
    """ Turns auto-renew on or off for all active loans """
    if toggle:
        toggle = 1
    else:
        toggle = 0
    for loan in api.returnActiveLoans()['provided']:
        if int(loan['autoRenew']) != toggle:
            logger.info('Toggling autorenew for offer %s', loan['id'])
            api.toggleAutoRenew(loan['id'])


def UTCstr2epoch(datestr, fmat="%Y-%m-%d %H:%M:%S"):
    """
    - takes UTC date string
    - returns epoch
    """
    return timegm(strptime(datestr, fmat))


class Loaner(object):
    """ Loanbot class [API REQUIRES KEY AND SECRET!]"""

    def __init__(self,
                 api,
                 coins={'BTC': 0.01},
                 maxage=60 * 30,
                 offset=6,
                 delay=60 * 10):
        self.api, self.delay, self.coins, self.maxage, self.offset =\
            api, delay, coins, maxage, offset
        # Check auto renew is not enabled for current loans
        autoRenewAll(self.api, toggle=False)

    def start(self):
        """ Start the thread """
        self.__process = Process(target=self.run)
        self.__process.daemon = True
        self._running = True
        self.__process.start()

    def stop(self):
        """ Stop the thread """
        self._running = False
        try:
            self.__process.join()
        except Exception as e:
            logger.exception(e)

    def getLoanOfferAge(self, order):
        return time() - UTCstr2epoch(order['date'])

    def cancelOldOffers(self):
        logger.info('Getting open loan offers')
        offers = self.api.returnOpenLoanOffers()
        for coin in self.coins:
            logger.info('Checking for "stale" %s loans...', OR(coin))
            if coin not in offers:
                logger.info('No open offers found.')
                continue
            for offer in offers[coin]:
                if self.getLoanOfferAge(offer) > self.maxage:
                    logger.info('Canceling %s offer %s',
                                OR(coin), GY(offer['id']))
                    logger.info(self.api.cancelLoanOffer(offer['id']))

    def createLoanOffers(self):
        logger.info('Getting account balances')
        bals = self.api.returnAvailableAccountBalances()
        if not 'lending' in bals:
            return logger.info('No coins found in lending account')
        for coin in self.coins:
            if coin not in bals['lending']:
                logger.info("No available %s in lending", OR(coin))
                continue
            amount = bals['lending'][coin]
            if float(amount) < self.coins[coin]:
                logger.info("Not enough %s:%s, below set minimum: %s",
                            OR(coin),
                            RD(str(amount)),
                            BL(str(self.coins[coin])))
                continue
            orders = self.api.returnLoanOrders(coin)['offers']
            topRate = float(orders[0]['rate'])
            price = topRate + (self.offset * loantoshi)
            logger.info('Creating %s %s loan offer at %s',
                        RD(str(amount)), OR(coin), GR(str(price)))
            logger.info(self.api.createLoanOffer(
                coin, amount, price, autoRenew=0))

    def run(self):
        """ Main loop, cancels 'stale' loan offers, turns auto-renew off on
        active loans, and creates new loan offers at optimum price """
        while self._running:
            try:
                # Check for old offers
                self.cancelOldOffers()
                # Create new offer (if can)
                self.createLoanOffers()
                # show active
                active = self.api.returnActiveLoans()['provided']
                logger.info(GR('Active Loans:----------------'))
                for i in active:
                    logger.info('%s|%s:%s-[rate:%s]-[fees:%s]',
                                BL(i['date']),
                                OR(i['currency']),
                                RD(i['amount']),
                                GY(str(float(i['rate']) * 100) + '%'),
                                GR(i['fees'])
                                )

            except Exception as e:
                logger.exception(e)

            finally:
                # sleep with one eye open...
                for i in range(int(self.delay)):
                    if not self._running:
                        break
                    sleep(1)

if __name__ == '__main__':
    from sys import argv
    logging.basicConfig(
        format='[%(asctime)s]%(message)s',
        datefmt=GR("%H:%M:%S"),
        level=logging.INFO
    )
    logging.getLogger('requests').setLevel(logging.ERROR)
    key, secret = argv[1:3]

    #################-Configure Below-##################################
    ########################
    # This dict defines what coins the bot should worry about
    # The dict 'key' is the coin to lend, 'value' is the minimum amount to lend
    coins = {
        'DASH': 1,
        'DOGE': 1000.0,
        'BTC': 0.1,
        'LTC': 1,
        'ETH': 1}

    # Maximum age (in secs) to let an open offer sit
    maxage = 60 * 30  # 30 min

    # number of loantoshis to offset from lowest asking rate
    offset = 6  # (6 * 0.000001)+lowestask

    # number of seconds between loops
    delay = 60 * 10  # 10 min

    ########################
    #################-Stop Configuring-#################################
    loaner = Loaner(Poloniex(key, secret, jsonNums=float),
                    coins, maxage, offset, delay)
    loaner.start()
    while loaner._running:
        try:
            sleep(1)
        except:
            loaner.stop()
            break
