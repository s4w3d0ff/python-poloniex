from subprocess import Popen, PIPE
from multiprocessing.dummy import Process as Thread
import json

import poloniex

class Ticker(object):
	""" Ticker object for controlling the ticker thread and subprocess
		Holds poloniex ticker dict under self.markets"""
	def __init__(self):
		self._tickerP, self._tickerT = [None, None]
		self.markets = poloniex.Poloniex().marketTicker()
		
	def startTicker(self):
		""" Starts the 'tickcatcher' subprocess and 'tickCatcher' thread"""
		self._tickerP = Popen(["python", "tickcatcher.py"], stdout=PIPE, bufsize=1)
		print('TICKER: tickcatcher subprocess started')
		
		self._tickerT = Thread(target=self.tickCatcher);self._tickerT.daemon = True
		self._tickerT.start()
		print('TICKER: tickCatcher thread started')
	
	def stopTicker(self):
		""" Stops the ticker subprocess"""
		self._tickerP.terminate();self._tickerP.kill()
		print('TICKER: Ticker subprocess stopped')
		self._tickerT.join()
		print('TICKER: Ticker thread joined')
	
	def tickCatcher(self):
		with self._tickerP.stdout:
			for line in iter(self._tickerP.stdout.readline, b''):
				try:
					tick = json.loads(line[25:]) # shave off twisted timestamp (probably a better way to remove the timestamp...)
					self.markets[tick[0]] = {
							'last':tick[1], 
							'lowestAsk':tick[2], 
							'highestBid':tick[3], 
							'percentChange':tick[4], 
							'baseVolume':tick[5], 
							'quoteVolume':tick[6], 
							'isFrozen':tick[7], 
							'high24hr':tick[8], 
							'low24hr':tick[9],
							'id':self.markets[tick[0]]['id']
							}
				except Exception as e:
					print(e)
				
		self._tickerP.wait()

if __name__ == "__main__":
	from time import sleep
	polo = Ticker()
	print(polo.markets['BTC_ETH'])
	polo.startTicker()
	sleep(20)
	polo.stopTicker()
	print(polo.markets['BTC_ETH'])
	#should output 2 different ticks for ETH (old and new)
