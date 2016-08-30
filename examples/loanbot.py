#!/usr/bin python
import time, logging
from multiprocessing.dummy import Process as Thread
from poloniex import Poloniex

class Loaner(object):
	""" Object for control of threaded Loaner loop"""
	def __init__(self, Key, Secret, interval=60*2, ageLimit=60*5, offset=2):
		"""
		- <Key> - Polo Api key
		- <Secret> - Polo Api secret
		- Loaner.INTERVAL = time in sec to wait between updates [default= 2min]
		- Loaner.AGELIMIT = max age (in sec) for an open loan offer [default= 5min]
		- Loaner.OFFSET = offset from the top loan offer rate (offset*0.000001) [default= 2]
		- Loaner.CHECKINT = number of times to check Loaner.RUNNING between intervals [default= INTERVAL/10]
		- Loaner.MINAMOUNT = Minimum amount for creating loan offers [default= 0.01]
		"""
		self.POLO = Poloniex(Key, Secret)
		self.INTERVAL, self.CHECKINT = interval, interval/10
		self.AGELIMIT, self.OFFSET,  self.MINAMOUNT = ageLimit, offset, 0.01
		self._running, self._thread = False, None

	def _run(self):
		""" Main loop that is threaded (set Loaner.RUNNING to 'False' to stop loop)"""
		while self._running:
			try:
				self.cancelOldLoans(self.POLO.myOpenLoanOrders(), self.AGELIMIT)
				self.createLoans(self.POLO.myAvailBalances(), self.OFFSET)
				for i in range(self.CHECKINT):
					if not self._running: break
					time.sleep(self.INTERVAL/self.CHECKINT)
			except Exception as e:
				logging.info(e);time.sleep(self.INTERVAL/self.CHECKINT)

	def start(self):
		""" Start Loaner.thread"""
		self._thread = Thread(target=self._run);self._thread.daemon = True
		self._running = True;self._thread.start()
		logging.info('LOANER: started')

	def stop(self):
		""" Stop Loaner.thread"""
		self._running = False;self._thread.join()
		logging.info('LOANER: stopped')

	def cancelOldLoans(self, orderList, ageLimit):
		""" Cancel loans in <orderList> that are older than <ageLimit>
			- orderList = JSON object received from poloniex (open loan orders)
			- ageLimit = max age to allow an order to sit still before canceling (in seconds)"""
		logging.info('LOANER: Checking for stale offers')
		for market in orderList:
			for order in orderList[market]:
				logging.info('LOANER: %s order %s has been open %f2 mins' % (
				        market,
				        str(order['id']),
				        round((time.time()-self.POLO.UTCstr2epoch(order['date']))/60, 2))
				        )
				if time.time()-self.POLO.UTCstr2epoch(order['date']) > ageLimit:
					result = self.POLO.cancelLoanOrder(order['id'])
					if not 'error' in result:
					    logging.info('LOANER: %s %s [%s]' % (
					            market,
					            result["message"].lower(),
					            str(order['id'])
					            ))
					else:
					    logging.info('LOANER: %s' % result['error'])

	def createLoans(self, balances, offset):
		""" Create loans for all markets in <balances> at the <offset> from the top rate
			- balances = JSON object received from poloniex (available balances)
			- offset = number of 'loanToshis' to offset from the top loan order (offset*0.000001)"""
		if 'lending' in balances:
			logging.info('LOANER: Checking for coins in lending account')
			for market in balances['lending']:
				if float(balances['lending'][market]) > self.MINAMOUNT:
					result = self.POLO.createLoanOrder(
					        market,
					        balances['lending'][market],
					        float(self.POLO.marketLoans(market)['offers'][0]['rate'])+(offset*0.000001)
					        )
					if not 'error' in result:
					    logging.info('LOANER: %s %s %s' % (
					            balances['lending'][market],
					            market,
					            result["message"].lower()
					            ))
					else:
					    logging.info('LOANER: %s' % result['error'])

if __name__ == "__main__":
    import argparse
    import sys
    logging.basicConfig(format='[%(asctime)s]%(message)s', datefmt="%H:%M:%S", level=logging.INFO)
    parser = argparse.ArgumentParser(description='A Simple Poloniex Loanbot!')
    parser.add_argument('apikey')
    parser.add_argument('apisecret')
    parser.add_argument(
            '--interval',
            nargs='?',
            const=60*2,
            default=60*2,
            help='time in sec to wait between updates [default= 2min]'
            )
    parser.add_argument(
            '--agelimit',
            nargs='?',
            const=60*5,
            default=60*5,
            help='max age (in sec) for an open loan offer [default= 5min]'
            )
    parser.add_argument(
            '--offset',
            nargs='?',
            const=2,
            default=2,
            help='offset from the top loan offer rate (offset*0.000001) [default= 2]'
            )
    args = parser.parse_args()
    bot = Loaner(
            args.apikey,
            args.apisecret,
            int(args.interval),
            int(args.agelimit),
            int(args.offset)
            )
    bot.start()
    while 1:
        try:
            time.sleep(0.5)
        except:
            bot.stop()
            sys.exit()
