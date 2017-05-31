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
            logger.info('Toggling autorenew for offer %s', str(loan['id']))
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
                 delay=60 * 10):
        self.api, self.delay, self.coins, self.maxage =\
            api, delay, coins, maxage

    def start(self):
        """ Start the thread """
        self._process = Process(target=self.run)
        self._process.daemon = True
        self._running = True
        self._process.start()

    def stop(self):
        """ Stop the thread """
        self._running = False
        try:
            self._process.join()
        except Exception as e:
            logger.exception(e)

    def getLoanOfferAge(self, order):
        return time() - UTCstr2epoch(order['date'])

    def cancelOldOffers(self):
        logger.info(GR("Checking Open Loan Offers:----------------"))
        offers = self.api.returnOpenLoanOffers()
        for coin in self.coins:
            if coin not in offers:
                logger.debug("No open %s offers found.", coin)
                continue
            for offer in offers[coin]:
                logger.info("%s|%s:%s-[rate:%s]",
                            BL(offer['date']),
                            OR(coin),
                            RD(offer['amount']),
                            GY(str(float(offer['rate']) * 100) + '%')
                            )
                if self.getLoanOfferAge(offer) > self.maxage:
                    logger.info("Canceling %s offer %s",
                                OR(coin), GY(str(offer['id'])))
                    logger.debug(self.api.cancelLoanOffer(offer['id']))

    def createLoanOffers(self):
        logger.info(GR("Checking for coins to lend:---------------"))
        bals = self.api.returnAvailableAccountBalances()
        if not 'lending' in bals:
            return logger.info(RD("No coins found in lending account"))
        for coin in self.coins:
            if coin not in bals['lending']:
                continue
            amount = bals['lending'][coin]
            if float(amount) < self.coins[coin]:
                logger.info("Not enough %s:%s, below set minimum: %s",
                            OR(coin),
                            RD(str(amount)),
                            BL(str(self.coins[coin])))
                continue
            else:
                logging.info("%s:%s", OR(coin), GR(str(amount)))
            orders = self.api.returnLoanOrders(coin)['offers']
            price = sum([float(o['rate']) for o in orders]) / len(orders)
            logger.info('Creating %s %s loan offer at %s',
                        RD(str(amount)), OR(coin), GR(str(price * 100) + '%'))
            r = self.api.createLoanOffer(coin, amount, price, autoRenew=0)
            logger.info('%s', GR(r["message"]))

    def run(self):
        """ Main loop, cancels 'stale' loan offers, turns auto-renew off on
        active loans, and creates new loan offers at optimum price """
        # Check auto renew is not enabled for current loans
        autoRenewAll(self.api, toggle=False)
        while self._running:
            try:
                # Check for old offers
                self.cancelOldOffers()
                # Create new offer (if can)
                self.createLoanOffers()
                # show active
                active = self.api.returnActiveLoans()['provided']
                logger.info(GR('Active Loans:-----------------------------'))
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
        level=logging.DEBUG
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
    maxage = 60 * 10  # 10 min

    # number of seconds between loops
    delay = 60 * 5  # 5 min

    ########################
    #################-Stop Configuring-#################################
    loaner = Loaner(Poloniex(key, secret, timeout=120, jsonNums=float),
                    coins, maxage, delay)
    loaner.start()
    while loaner._running:
        try:
            sleep(1)
        except:
            loaner.stop()
            break
