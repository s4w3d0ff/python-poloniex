from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
import json

#import sys;sys.path.append("..") # uncomment if running the script from the 'examples' folder and did not manualy install poloniex.py
import poloniex

# Catches the push messages from polo ticker and saves them to a json file

class Subscribe2Ticker(ApplicationSession):
	@inlineCallbacks
	def onJoin(self, details):
		TICKER = poloniex.Poloniex().marketTicker() # fill the local ticker dict with latest ticker data
		saveJSON(TICKER,'ticker') # save ticker as json file (for use in other programs like Conky)
		def onTick(*args): # everytime we get a push message from the polo ticker
			# update local ticker with received data
			TICKER[args[0]] = {	'last':args[1], 
						'lowestAsk':args[2], 
						'highestBid':args[3], 
						'percentChange':args[4], 
						'baseVolume':args[5], 
						'quoteVolume':args[6], 
						'isFrozen':args[7], 
						'24hrHigh':args[8], 
						'24hrLow':args[9]}
			# save/overwrite local ticker json file
			saveJSON(TICKER,'ticker')
		yield self.subscribe(onTick, 'ticker')


def saveJSON(data, fileName):
	with open(fileName+'.json', 'w+') as f:
		json.dump(data, f, sort_keys=True, indent=4)

if __name__ == "__main__":
	subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1")
	subscriber.run(Subscribe2Ticker)
