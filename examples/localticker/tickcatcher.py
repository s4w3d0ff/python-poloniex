from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
import json

def onTick(*args): # everytime we get a push message from the polo ticker
	print(json.dumps(args)) # send json string to stdout

class Subscribe2Ticker(ApplicationSession):
	@inlineCallbacks
	def onJoin(self, details):
		yield self.subscribe(onTick, 'ticker')

if __name__ == "__main__":
	subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1")
	subscriber.run(Subscribe2Ticker)
