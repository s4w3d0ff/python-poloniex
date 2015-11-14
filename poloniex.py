import json
import time
import hmac, hashlib
import sys
from datetime import datetime

# Tested on Python 2.7.6 & 3.4.3
if sys.version_info[0] == 3:
	from urllib.request import Request, urlopen
	from urllib.parse import urlencode
else:
	from urllib2 import Request, urlopen
	from urllib import urlencode

minute = 60
hour = minute*60
day = hour*24
week = day*7
month = day*30
year = day*365

# Possible Commands
PUBLIC_COMMANDS = ['returnTicker', 'return24hVolume', 'returnOrderBook', 'returnTradeHistory', 'returnChartData', 'returnCurrencies', 'returnLoanOrders'] 
PRIVATE_COMMANDS = ['returnBalances', 'returnCompleteBalances', 'returnDepositAddresses', 'generateNewAddress', 'returnDepositsWithdrawals', 'returnOpenOrders', 'returnTradeHistory', 'returnAvailableAccountBalances', 'returnTradableBalances', 'returnOpenLoanOffers', 'returnActiveLoans', 'createLoanOffer', 'cancelLoanOffer', 'toggleAutoRenew', 'buy', 'sell', 'cancelOrder', 'moveOrder', 'withdraw', 'transferBalance', 'returnMarginAccountSummary', 'marginBuy', 'marginSell', 'getMarginPosition', 'closeMarginPosition']

class Poloniex:
	def __init__(self, APIKey='', Secret=''):
		self.APIKey = APIKey
		self.Secret = Secret
		# Conversions
		self.timestamp_str = lambda timestamp=time.time(), format="%Y-%m-%d %H:%M:%S": datetime.fromtimestamp(timestamp).strftime(format)
		self.str_timestamp = lambda datestr=self.timestamp_str(), format="%Y-%m-%d %H:%M:%S": int(time.mktime(time.strptime(datestr, format)))
		self.float_roundPercent = lambda floatN, decimalP=2: str(round(float(floatN)*100, decimalP))+"%"
		
		#PUBLIC COMMANDS
		self.marketTicker = lambda x=0: self.api('returnTicker')
		self.marketVolume = lambda x=0: self.api('return24hVolume')
		self.marketStatus = lambda x=0: self.api('returnCurrencies')
		self.marketLoans = lambda coin: self.api('returnLoanOrders',{'currency':coin})
		self.marketOrders = lambda pair='all': self.api('returnOrderBook', {'currencyPair':pair})
		self.marketChart = lambda pair, period=day, start=time.time()-(month*2), end=time.time(): self.api('returnChartData', {'currencyPair':pair, 'period':period, 'start':start, 'end':end})
		self.marketTradeHist = lambda pair: self.api('returnTradeHistory',{'currencyPair':pair}) # NEEDS TO BE FIXED ON Poloniex
		
		#PRIVATE COMMANDS
		#self.myTradeHist = lambda pair: self.api('returnTradeHistory',{'currencyPair':pair})
		self.myAvailBalances = lambda x=0: self.api('returnAvailableAccountBalances')
		self.myMarginAccountSummary = lambda x=0: self.api('returnMarginAccountSummary')
		self.myMarginPosition = lambda pair='all': self.api('getMarginPosition',{'currencyPair':pair})
		self.myCompleteBalances = lambda x=0: self.api('returnCompleteBalances')
		self.myAddresses = lambda x=0: self.api('returnDepositAddresses')
		self.myOrders = lambda pair='all': self.api('returnOpenOrders',{'currencyPair':pair})
		self.myDepositsWithdraws = lambda x=0: self.api('returnDepositsWithdrawals')
		self.myTradeableBalances = lambda x=0: self.api('returnTradableBalances')
		self.myActiveLoans = lambda x=0: self.api('returnActiveLoans')
		self.myOpenLoanOrders = lambda x=0: self.api('returnOpenLoanOffers')
		## Trading functions ##
		self.createLoanOrder = lambda coin, amount, rate: self.api('createLoanOffer', {'currency' :coin, 'amount':amount, 'duration':2, 'autoRenew':0, 'lendingRate':rate})
		self.cancelLoanOrder = lambda orderId: self.api('cancelLoanOffer', {'orderNumber':orderId})
		self.toggleAutoRenew = lambda orderId: self.api('toggleAutoRenew', {'orderNumber':orderId})
		self.closeMarginPosition = lambda pair: self.api('closeMarginPosition',{'currencyPair':pair})
		self.marginBuy = lambda pair, rate, amount, lendingRate=2: self.api('marginBuy',{'currencyPair':pair, 'rate':rate, 'amount':amount, 'lendingRate':lendingRate})
		self.marginSell= lambda pair, rate, amount, lendingRate=2: self.api('marginSell',{'currencyPair':pair, 'rate':rate, 'amount':amount, 'lendingRate':lendingRate})
		self.buy = lambda pair, rate, amount: self.api('buy', {'currencyPair':pair, 'rate':rate, 'amount':amount})
		self.sell = lambda pair, rate, amount: self.api('sell', {'currencyPair':pair, 'rate':rate, 'amount':amount})
		self.cancelOrder = lambda orderId: self.api('cancelOrder', {'orderNumber':orderId})
		self.moveOrder = lambda orderId, rate, amount: self.api('moveOrder', {'orderNumber':orderId, 'rate':rate, 'amount':amount})
		self.withdraw = lambda coin, amount, address: self.api('withdraw', {'currency':coin, 'amount':amount, 'address':address})
		self.transferBalance = lambda coin, amount, fromac, toac: self.api('transferBalance', {'currency':coin, 'amount':amount, 'fromAccount':fromac, 'toAccount':toac})
		
	#####################
	# Main Api Function #
	#####################
	def api(self, command, args={}):
		"""
		returns 'False' if invalid command or if no APIKey or Secret is specified (if command is "private")
		returns {"error":"<error message>"} if API error
		"""
		args['command'] = command
		if command in PRIVATE_COMMANDS:
			if len(self.APIKey) < 2 or len(self.Secret) < 2:
				print("An APIKey and Secret is needed!")
				return False
			url, args['nonce'] = ['https://poloniex.com/tradingApi', int(time.time()*42)]
			post_data = urlencode(args)
			sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
			headers = {'Sign': sign, 'Key': self.APIKey}
			ret = urlopen(Request(url, post_data, headers))
			return json.loads(ret.read().decode(encoding='UTF-8'))
		elif command in PUBLIC_COMMANDS:
			url = 'https://poloniex.com/public?'
			if not args:
				ret = urlopen(Request(url + command))
				return json.loads(ret.read().decode(encoding='UTF-8'))
			else:
				ret = urlopen(Request(url + urlencode(args)))
				return json.loads(ret.read().decode(encoding='UTF-8'))
		else:return False
