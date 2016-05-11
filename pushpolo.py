from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
import logging, logging.handlers
from HTMLParser import HTMLParser

logging.basicConfig(format='%(message)s' ,level=logging.DEBUG)
trolllogger = logging.getLogger()
trolllogger.addHandler(logging.handlers.RotatingFileHandler('TrollBox.log', maxBytes=10**9, backupCount=5)) # makes 1Gb log files, 5 files max

class Subscribe2Trollbox(ApplicationSession):
	@inlineCallbacks
	def onJoin(self, details):
		h = HTMLParser()
		def onTroll(*args):
			try:
				logging.info('%s:%s:: (%s)-%s- %s' % (args[0].upper(), str(args[1]), str(args[4]), args[2], h.unescape(args[3]) ))
			except IndexError: # Sometimes its a banhammer!
				#(u'trollboxMessage', 6943543, u'Banhammer', u'OldManKidd banned for 0 minutes by OldManKidd.')
				logging.info('%s:%s:: -%s- %s' % (args[0].upper(), str(args[1]), args[2], h.unescape(args[3]) ))
		yield self.subscribe(onTroll, 'trollbox')

if __name__ == "__main__":
	subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1")
	subscriber.run(Subscribe2Trollbox)
