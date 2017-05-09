from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
import logging, logging.handlers
import sys
if sys.version_info[0] is 3:
	from html.parser import HTMLParser
else:
	from HTMLParser import HTMLParser
logging.basicConfig(format='[%(asctime)s]%(message)s', datefmt="%H:%M:%S", level=logging.INFO)
trolllogger = logging.getLogger()
trolllogger.addHandler(logging.handlers.RotatingFileHandler('TrollBox.log', maxBytes=10**9, backupCount=5)) # makes 1Gb log files, 5 files max

W  = '\033[0m'  # white (normal)
R  = lambda text: '\033[31m'+text+W # red
G  = lambda text: '\033[32m'+text+W # green
O  = lambda text: '\033[33m'+text+W # orange
B  = lambda text: '\033[34m'+text+W # blue
P  = lambda text: '\033[35m'+text+W # purp
C  = lambda text: '\033[36m'+text+W # cyan
GR = lambda text: '\033[37m'+text+W # gray

class Subscribe2Trollbox(ApplicationSession):
	@inlineCallbacks
	def onJoin(self, details):
		h = HTMLParser()
		self.alter = True
		self.name = 'PulloutKing'
		self.mods = {
			"Xoblort": 1,
			"Chickenliver": 1,
			"MobyDick": 1,
			"cybiko123": 1,
			"SweetJohnDee": 1,
			"smallbit": 1,
			"Wizwa": 1,
			"OldManKidd": 1,
			"Quantum": 1,
			"Popcorntime": 1,
			"busoni@poloniex": 1,
			"Thoth": 1,
			"wausboot": 1,
			"Mirai": 1,
			"qubix": 1,
			"Oldgamejunk": 1,
			"Chewpacabra": 1,
			"orio": 1,
			"j33hopper": 1,
			"VenomGhost": 1,
			"ultim8um": 1,
			"TheDjentleman": 1,
			"GambitKnight": 1,
			"Bigolas": 1,
			"Watchtower": 1
		}

		self.friends = [] # :.(
		def onTroll(*args):
			try:
				logging.debug(args[0].upper(), str(args[1]))
				name = args[2]
				message = h.unescape(args[3])
				# Name coloring
				if name == self.name: # own name is green
					name = G(name)
				elif name in self.friends: # friends are purple
					name = P(name)
				elif name in self.mods: # mods are orange
					name = O(name)
				else:
					name = C(name) # others are cyan
				# Message Coloring
				if self.name in message: # mentions are green
					message = G(message)
				elif 'POLO TIP' in message: #(supposed) polo tips are blue
					message = B(message)
				# other messages alternate from 'normal' to gray
				elif self.alter:
					message = GR(message)
					self.alter = False
				else:
					message = message
					self.alter = True
				logging.info('%s(%s): %s' % (name, B(str(args[4])), message))
			except IndexError: # Sometimes its a banhammer!
				#(u'trollboxMessage', 6943543, u'Banhammer', u'OldManKidd banned for 0 minutes by OldManKidd.')
				logging.info('%s %s' % (R(name), R(message) ))
				
		yield self.subscribe(onTroll, 'trollbox')


if __name__ == "__main__":
	subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1")
	subscriber.run(Subscribe2Trollbox)
