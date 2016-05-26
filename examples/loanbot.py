import time
from multiprocessing.dummy import Process as Thread
from poloniex import Poloniex
# Most attributes of the Loaner object can be changed "on the fly"
# Useage:
# >> import loanbot
# >> bot = loanbot.Loaner('yourPOLOAPIkey','yourSuperAPISecret')
# >> bot.start()
# LOANER: started
# LOANER: Checking for stale offers
# LOANER: BTS order 84776305 has been open 4.360000 mins
# LOANER: Checking for coins in account
# LOANER: Checking for stale offers
# LOANER: BTS order 84776305 has been open 6.550000 mins
# LOANER: BTS loan offer canceled. [84776305]
# LOANER: Checking for coins in account
# LOANER: 2249.160702 BTS loan order placed.
# LOANER: Checking for stale offers
# LOANER: BTS order 84780014 has been open 2.170000 mins

class Loaner(object):
	""" Object for control of threaded Loaner loop"""
	def __init__(self, Key, Secret, interval=60*2, ageLimit=60*5, offset=2):
		"""
		- <Key> - Polo Api key
		- <Secret> - Polo Api secret
		- Loaner.RUNNING = bool (set to 'False' to stop main thread)
		- Loaner.INTERVAL = time in sec to wait between updates [default= 2min]
		- Loaner.AGELIMIT = max age (in sec) for an open loan offer [default= 5min]
		- Loaner.OFFSET = offset from the top loan offer rate (offset*0.000001) [default= 2]
		- Loaner.CHECKINT = number of times to check Loaner.RUNNING between intervals (could be hard on cpu if set too high and INTERVAL set too low!) [default= 20]
		- Loaner.MINAMOUNT = Minimum amount for creating loan offers [default= 0.01]
		"""
		self.POLO = Poloniex(Key, Secret)
		self.INTERVAL, self.AGELIMIT, self.OFFSET, self.CHECKINT, self.MINAMOUNT, self.RUNNING = [interval, ageLimit, offset, 20, 0.01, False]
		self.thread = Thread(target=self.run);self.thread.daemon = True
	
	def run(self):
		""" Main loop that is threaded (set Loaner.RUNNING to 'False' to stop loop)"""
		while self.RUNNING:
			try:
				self.cancelOldLoans(self.POLO.myOpenLoanOrders(), self.AGELIMIT)
				self.createLoans(self.POLO.myAvailBalances(), self.OFFSET)
				for i in range(self.CHECKINT):
					if not self.RUNNING: break
					time.sleep(self.INTERVAL/self.CHECKINT)
			except Exception as e: 
			# Sometimes (when losing connection) the loop will 'stall' from urlopen (in poloniex) and I have not figured out a way to capture it yet....
			# maybe a 'timeout' setting in the revive socket will help...
				print(e);time.sleep(self.INTERVAL/self.CHECKINT)
	
	def start(self):
		""" Start Loaner.thread"""
		self.RUNNING = True;self.thread.start()
		print('LOANER: started')
	
	def stop(self):
		""" Stop Loaner.thread"""
		self.RUNNING = False;self.thread.join()
		print('LOANER: stopped')
	
	def cancelOldLoans(self, orderList, ageLimit):
		""" Cancel loans in <orderList> that are older than <ageLimit>
			- orderList = JSON object received from poloniex (open loan orders)
			- ageLimit = max age to allow an order to sit still before canceling (in seconds)""" 
		print('LOANER: Checking for stale offers')
		for market in orderList:
			for order in orderList[market]:
				print('LOANER: %s order %s has been open %f mins' % (market, str(order['id']), round((time.time()-self.POLO.UTCstr2epoch(order['date']))/60, 2)))
				if time.time()-self.POLO.UTCstr2epoch(order['date']) > ageLimit:
					result = self.POLO.cancelLoanOrder(order['id'])
					if not 'error' in result: print('LOANER: %s %s [%s]' % (market, result["message"].lower(), str(order['id'])))
					else: print('LOANER: %s' % result['error'])
	
	def createLoans(self, balances, offset):
		""" Create loans for all markets in <balances> at the <offset> from the top rate
			- balances = JSON object received from poloniex (available balances)
			- offset = number of 'loanToshis' to offset from the top loan order (offset*0.000001)""" 
		if 'lending' in balances:
			print('LOANER: Checking for coins in account')
			for market in balances['lending']:
				if float(balances['lending'][market]) > self.MINAMOUNT:
					result = self.POLO.createLoanOrder(market, balances['lending'][market], float(self.POLO.marketLoans(market)['offers'][0]['rate'])+(offset*0.000001))
					if not 'error' in result: print('LOANER: %f %s %s' % (float(balances['lending'][market]), market, result["message"].lower()))
					else: print('LOANER: %s' % result['error'])
