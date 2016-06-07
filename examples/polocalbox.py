from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
import logging, logging.handlers
from HTMLParser import HTMLParser

logging.basicConfig(format='[%(asctime)s]%(message)s', datefmt="%H:%M:%S", level=logging.INFO)
trolllogger = logging.getLogger()
trolllogger.addHandler(logging.handlers.RotatingFileHandler('TrollBox.log', maxBytes=10**9, backupCount=5)) # makes 1Gb log files, 5 files max

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple
C  = '\033[36m' # cyan
GR = '\033[37m' # gray

class Subscribe2Trollbox(ApplicationSession):
	@inlineCallbacks
	def onJoin(self, details):
		h = HTMLParser()
		self.alternator = True
		def onTroll(*args):
			try:
				logging.info('%s(%s)%s%s:%s %s' % (R, str(args[4]), O, args[2], W, h.unescape(args[3]) ))
			except IndexError: # Sometimes its a banhammer!
				#(u'trollboxMessage', 6943543, u'Banhammer', u'OldManKidd banned for 0 minutes by OldManKidd.')
				logging.info('%s%s%s %s' % (R, args[2], W, h.unescape(args[3]) ))
			finally:
				logging.debug(args[0].upper(), str(args[1]))
		yield self.subscribe(onTroll, 'trollbox')


if __name__ == "__main__":
	subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1")
	subscriber.run(Subscribe2Trollbox)
