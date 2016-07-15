# Poloniex API wrapper for Python 2.7 and 3 - https://github.com/s4w3d0ff/python-poloniex
# BTC: 15D8VaZco22GTLVrFMAehXyif6EGf8GMYV
import sys, logging, json, time, calendar
import hmac, hashlib
import requests

# Tested on Python 2.7.6 & 3.4.3
## TODO: Find out if request module has the equivalent...
if sys.version_info[0] == 3:from urllib.parse import urlencode
else:from urllib import urlencode

# Possible Commands
PUBLIC_COMMANDS = [
	'returnTicker',
	'return24hVolume', 
	'returnOrderBook', 
	'returnTradeHistory', 
	'returnChartData', 
	'returnCurrencies', 
	'returnLoanOrders']
	 
PRIVATE_COMMANDS = [
	'returnBalances', 
	'returnCompleteBalances', 
	'returnDepositAddresses', 
	'generateNewAddress', 
	'returnDepositsWithdrawals', 
	'returnOpenOrders', 
	'returnTradeHistory', 
	'returnAvailableAccountBalances', 
	'returnTradableBalances', 
	'returnOpenLoanOffers',
	'returnOrderTrades',
	'returnActiveLoans',
	'createLoanOffer', 
	'cancelLoanOffer', 
	'toggleAutoRenew', 
	'buy', 
	'sell', 
	'cancelOrder', 
	'moveOrder', 
	'withdraw', 
	'returnFeeInfo', 
	'transferBalance', 
	'returnMarginAccountSummary', 
	'marginBuy', 
	'marginSell', 
	'getMarginPosition', 
	'closeMarginPosition']

class Poloniex(object):
	"""The Poloniex Object!"""
	def __init__(self, APIKey='', Secret='', timeout=3, coach=False, loglevel=logging.WARNING,):
		"""
		APIKey = self.APIKey = str api key supplied by Poloniex
		Secret = self.Secret = str secret hash supplied by Poloniex
		timeout = self.timeout = int time in sec to wait for an api response (otherwise 'requests.exceptions.Timeout' is raised)
		coach = self._coaching = bool to indicate if the api coach should be used
		loglevel = logging level object to set the module at (changes the requests module as well)
		
		self.apiCoach = object that regulates spacing between api calls
		
		# Time Placeholders # (MONTH == 30*DAYS)
		
		self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.YEAR
		
		
		# Time Traveling Lambdas #
		
		self.epoch2UTCstr(timestamp=time.time(), fmat="%Y-%m-%d %H:%M:%S")
		- takes epoch timestamp
		- returns UTC formated string
		
		self.UTCstr2epoch(datestr=self.epoch2UTCstr(), fmat="%Y-%m-%d %H:%M:%S")
		- takes UTC date string
		- returns epoch
		
		self.epoch2localstr(timestamp=time.time(), fmat="%Y-%m-%d %H:%M:%S")
		- takes epoch timestamp
		- returns localtimezone formated string
		
		self.localstr2epoch(datestr=self.epoch2UTCstr(), fmat="%Y-%m-%d %H:%M:%S")
		- takes localtimezone date string, 
		- returns epoch
		
		
		# Conversions #
		
		self.float2roundPercent(float, decimalP=2)
		- takes float
		- returns percent(*100) rounded to the Nth decimal place as a string
		
		
		# Oh my lambdas! #
		
		# Public-------------------------
		self.marketTicker() == self.api('returnTicker')
		- returns the ticker for all markets
		
		self.marketVolume() == self.api('return24hVolume')
		- returns the volume data for all markets
		
		self.marketStatus() == self.api('returnCurrencies')
		- returns additional market info for all markets
		
		self.marketLoans(coin) == self.api('returnLoanOrders',{'currency':<coin>})
		- returns open loan orders for <coin>
		
		self.marketOrders(pair='all', depth=20) == self.api('returnOrderBook', {'currencyPair':[pair='all'], 'depth':[depth=20]})
		- returns orderbook for [pair='all'] at a depth of [depth=20] orders
		
		self.marketChart(pair, period=self.DAY, start=time.time()-self.YEAR, end=time.time()) == self.api('returnChartData', {'currencyPair':<pair>, 'period':[period=self.DAY], 'start':[start=time.time()-self.YEAR], 'end':[end=time.time()]})
		- returns chart data for <pair> with a candle period of [period=self.DAY] starting from [start=time.time()-self.YEAR] and ending at [end=time.time()]
		
		# Private-------------------------
		self.myTradeHist(pair) == self.api('returnTradeHistory',{'currencyPair':<pair>})
		- returns your private trade history for <pair>
		
		self.myBalances() == polo.api('returnBalances')
		- returns coin balances
		
		self.myAvailBalances() == self.api('returnAvailableAccountBalances')
		- returns your available account balances
		
		self.myMarginAccountSummary() == self.api('returnMarginAccountSummary')
		- returns your margin account summary
		
		self.myMarginPosition(pair='all') == self.api('getMarginPosition',{'currencyPair':[pair='all']})
		- returns your margin position for [pair='all']
		
		self.myCompleteBalances() == self.api('returnCompleteBalances')
		- returns your complete balances
		
		self.myAddresses() == self.api('returnDepositAddresses')
		- returns your deposit addresses 
		
		self.myOrders(pair='all') == self.api('returnOpenOrders',{'currencyPair':[pair='all']})
		- returns your open orders for [pair='all']
		
		self.myDepositsWithdraws() == self.api('returnDepositsWithdrawals')
		- returns your deposit/withdraw history
		
		self.myTradeableBalances() == self.api('returnTradableBalances')
		- returns your tradable balances
		
		self.myActiveLoans() == self.api('returnActiveLoans')
		- returns your active loans
		
		self.myOpenLoanOrders() == self.api('returnOpenLoanOffers')
		- returns your open loan offers
		
		self.orderTrades == self.api('returnOrderTrades',{'orderNumber':str(orderId)})
		- returns any trades made from <orderId>
		
		self.createLoanOrder(coin, amount, rate) == self.api('createLoanOffer', {'currency' :<coin>, 'amount':<amount>, 'duration':2, 'autoRenew':0, 'lendingRate':<rate>})
		- creates a loan offer for <coin> for <amount> at <rate>
		
		self.cancelLoanOrder(orderId) == self.api('cancelLoanOffer', {'orderNumber':<orderId>})
		- cancels the loan offer with <orderId>
		
		self.toggleAutoRenew(orderId) == self.api('toggleAutoRenew', {'orderNumber':<orderId>})
		- toggles the 'autorenew' feature on an <orderId> 
		
		self.closeMarginPosition(pair) == self.api('closeMarginPosition',{'currencyPair':<pair>})
		- closes the margin position on <pair>
		
		self.marginBuy(pair, rate, amount, lendingRate=2) == self.api('marginBuy', {'currencyPair':<pair>, 'rate':<rate>, 'amount':<amount>, 'lendingRate':[lendingRate=2]})
		- creates a margin buy order for <pair> at <rate> for <amount> with [lendingRate=2]%
		
		self.marginSell(pair, rate, amount, lendingRate=2) == self.api('marginSell', {'currencyPair':<pair>, 'rate':<rate>, 'amount':<amount>, 'lendingRate':[lendingRate=2]})
		- creates a margin sell order for <pair> at <rate> for <amount> with [lendingRate=2]%
		
		self.buy(pair, rate, amount) == self.api('buy', {'currencyPair':<pair>, 'rate':<rate>, 'amount':<amount>})
		- creates buy order for <pair> at <rate> for <amount>
		
		self.sell(pair, rate, amount) == self.api('sell', {'currencyPair':<pair>, 'rate':<rate>, 'amount':<amount>})
		- creates sell order for <pair> at <rate> for <amount>
		
		self.cancelOrder(orderId) == self.api('cancelOrder', {'orderNumber':<orderId>})
		- cancels order <orderId>
		
		self.moveOrder(orderId, rate, amount) == self.api('moveOrder', {'orderNumber':<orderId>, 'rate':<rate>, 'amount':<amount>})
		- moves order <orderId> to <rate> for <amount>
		
		self.withdraw(coin, amount, address) == self.api('withdraw', {'currency':<coin>, 'amount':<amount>, 'address':<address>})
		- withdraws <coin> <amount> to <address>
		
		self.returnFeeInfo() == self.api('returnFeeInfo')
		- return current trading fees and trailing 30-day volume in BTC
		
		self.transferBalance(coin, amount, fromac, toac) == self.api('transferBalance', {'currency':<coin>, 'amount':<amount>, 'fromAccount':<fromac>, 'toAccount':<toac>})
		- moves <coin> <amount> from <fromac> to <toac>
		"""
		# Set wrapper logging level
		logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt="%H:%M:%S", level=loglevel)
		# Suppress the requests	module logging output
		logging.getLogger("requests").setLevel(loglevel)
		logging.getLogger("urllib3").setLevel(loglevel)
		# Call coach, set nonce
		self.apiCoach, self.nonce = [Coach(), int(time.time())]
		# Grab keys, set timeout, ditch coach?
		self.APIKey, self.Secret, self.timeout, self._coaching = [APIKey, Secret, timeout, coach]
		# Set time labels
		self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.YEAR = [60, 60*60, 60*60*24, 60*60*24*7, 60*60*24*30, 60*60*24*365]
		# Convertions
		self.epoch2UTCstr = lambda timestamp=time.time(), fmat="%Y-%m-%d %H:%M:%S": time.strftime(fmat, time.gmtime(timestamp))
		self.UTCstr2epoch = lambda datestr=self.epoch2UTCstr(), fmat="%Y-%m-%d %H:%M:%S": calendar.timegm(time.strptime(datestr, fmat))
		self.epoch2localstr = lambda timestamp=time.time(), fmat="%Y-%m-%d %H:%M:%S": time.strftime(fmat, time.localtime(timestamp))
		self.localstr2epoch = lambda datestr=self.epoch2localstr(), fmat="%Y-%m-%d %H:%M:%S": time.mktime(time.strptime(datestr, fmat))
		self.float2roundPercent = lambda floatN, decimalP=2: str(round(float(floatN)*100, decimalP))+"%"
		#PUBLIC COMMANDS
		self.marketTicker = lambda x=0: self.api('returnTicker')
		self.marketVolume = lambda x=0: self.api('return24hVolume')
		self.marketStatus = lambda x=0: self.api('returnCurrencies')
		self.marketLoans = lambda coin: self.api('returnLoanOrders',{'currency':str(coin)})
		self.marketOrders = lambda pair='all', depth=20: self.api('returnOrderBook', {'currencyPair':str(pair), 'depth':str(depth)})
		self.marketChart = lambda pair, period=self.DAY, start=time.time()-self.YEAR, end=time.time(): self.api('returnChartData', {'currencyPair':str(pair), 'period':str(period), 'start':str(start), 'end':str(end)})
		#PRIVATE COMMANDS
		self.myTradeHist = lambda pair: self.api('returnTradeHistory',{'currencyPair':str(pair)})
		self.myBalances = lambda x=0: self.api('returnBalances')
		self.myAvailBalances = lambda x=0: self.api('returnAvailableAccountBalances')
		self.myMarginAccountSummary = lambda x=0: self.api('returnMarginAccountSummary')
		self.myMarginPosition = lambda pair='all': self.api('getMarginPosition',{'currencyPair':str(pair)})
		self.myCompleteBalances = lambda x=0: self.api('returnCompleteBalances')
		self.myAddresses = lambda x=0: self.api('returnDepositAddresses')
		self.myOrders = lambda pair='all': self.api('returnOpenOrders',{'currencyPair':str(pair)})
		self.myDepositsWithdraws = lambda x=0: self.api('returnDepositsWithdrawals')
		self.myTradeableBalances = lambda x=0: self.api('returnTradableBalances')
		self.myActiveLoans = lambda x=0: self.api('returnActiveLoans')
		self.myOpenLoanOrders = lambda x=0: self.api('returnOpenLoanOffers')
		## Trading functions ##
		self.orderTrades = lambda orderId: self.api('returnOrderTrades',{'orderNumber':str(orderId)})
		self.createLoanOrder = lambda coin, amount, rate: self.api('createLoanOffer', {'currency' :str(coin), 'amount':str(amount), 'duration':str(2), 'autoRenew':str(0), 'lendingRate':str(rate)})
		self.cancelLoanOrder = lambda orderId: self.api('cancelLoanOffer', {'orderNumber':str(orderId)})
		self.toggleAutoRenew = lambda orderId: self.api('toggleAutoRenew', {'orderNumber':str(orderId)})
		self.closeMarginPosition = lambda pair: self.api('closeMarginPosition',{'currencyPair':str(pair)})
		self.marginBuy = lambda pair, rate, amount, lendingRate=2: self.api('marginBuy', {'currencyPair':str(pair), 'rate':str(rate), 'amount':str(amount), 'lendingRate':str(lendingRate)})
		self.marginSell= lambda pair, rate, amount, lendingRate=2: self.api('marginSell', {'currencyPair':str(pair), 'rate':str(rate), 'amount':str(amount), 'lendingRate':str(lendingRate)})
		self.buy = lambda pair, rate, amount: self.api('buy', {'currencyPair':str(pair), 'rate':str(rate), 'amount':str(amount)})
		self.sell = lambda pair, rate, amount: self.api('sell', {'currencyPair':str(pair), 'rate':str(rate), 'amount':str(amount)})
		self.cancelOrder = lambda orderId: self.api('cancelOrder', {'orderNumber':str(orderId)})
		self.moveOrder = lambda orderId, rate, amount: self.api('moveOrder', {'orderNumber':str(orderId), 'rate':str(rate), 'amount':str(amount)})
		self.withdraw = lambda coin, amount, address: self.api('withdraw', {'currency':str(coin), 'amount':str(amount), 'address':str(address)})
		self.returnFeeInfo = lambda x=0: self.api('returnFeeInfo')
		self.transferBalance = lambda coin, amount, fromac, toac: self.api('transferBalance', {'currency':str(coin), 'amount':str(amount), 'fromAccount':str(fromac), 'toAccount':str(toac)})
	
	def marketTradeHist(self, pair, start, end=time.time()):
		"""
		returns public trade history for <pair> starting at <start> and ending at [end=time.time()]
		"""
		try:
			if self._coaching: self.apiCoach.wait()
			ret = requests.post('https://poloniex.com/public?'+urlencode({'command':'returnTradeHistory', 'currencyPair':str(pair), 'start':str(start), 'end':str(end)}), timeout=self.timeout)
			return json.loads(ret.text)
		except Exception as e:raise e
	
	def api(self, command, args={}):
		"""
		Main Api Function
		- encodes and sends <command> with optional [args] to Poloniex api
		- raises 'ValueError' if an api key or secret is missing (and the command is 'private'), or if the <command> is not valid
		- returns decoded json api message
		"""
		if self._coaching: self.apiCoach.wait() # check in with the coach
		args['command'] = command # pass the command
		
		global PUBLIC_COMMANDS;global PRIVATE_COMMANDS
		
		if command in PRIVATE_COMMANDS: # private?
			try:
				if len(self.APIKey) < 2 or len(self.Secret) < 2:
					raise ValueError("An APIKey and Secret is needed for private api commands!")
				args['nonce'] = self.nonce
				post_data = urlencode(args)
				sign = hmac.new(self.Secret.encode('utf-8'), post_data.encode('utf-8'), hashlib.sha512).hexdigest()
				headers = {'Sign': sign, 'Key': self.APIKey}
				ret = requests.post('https://poloniex.com/tradingApi', data=args, headers=headers, timeout=self.timeout)
				return json.loads(ret.text)
			except Exception as e:raise e
			finally:self.nonce+=1 # increment nonce
			
		elif command in PUBLIC_COMMANDS: # public?
			try:
				ret = requests.post('https://poloniex.com/public?' + urlencode(args), timeout=self.timeout)
				return json.loads(ret.text)
			except Exception as e:raise e
		else:raise ValueError("Invalid Command!")
	

class Coach(object):
	"""
	Coaches the api wrapper, to make sure it doesn't get all hyped up on Mt.Dew and go over Poloniex api call limit.
	Poloniex default call limit is 6 calls per 1 sec.
	"""
	def __init__(self, timeFrame=1.0, callLimit=6):
		"""
		timeFrame = self._timeFrame = float time in secs [default = 1.0]
		callLimit = self._callLimit = int max amount of calls per 'timeFrame' [default = 6]
		"""
		self._timeFrame, self._callLimit, self._timeBook = [timeFrame, callLimit, []]
			
	def wait(self):
		"""
		Make sure our api calls don't go past the api call limit
		"""
		now = time.time() # what time is it?
		if len(self._timeBook) == 0 or (now - self._timeBook[-1]) >= self._timeFrame: # if it's your turn
			self._timeBook.insert(0, now) # add 'now' to the front of 'timeBook', pushing other times back
			logging.info("Now: %d  Oldest Call: %d  Diff: %f sec" % (now, self._timeBook[-1], now - self._timeBook[-1]))
			if len(self._timeBook) > self._callLimit:self._timeBook.pop() # remove the oldest time if 'timeBook' list is larger than 'callLimit'
		else:
			logging.info("Now: %d  Oldest Call: %d  Diff: %f sec" % (now, self._timeBook[-1], now - self._timeBook[-1]))
			logging.info("Waiting %s sec..." % str(self._timeFrame-(now - self._timeBook[-1])))
			time.sleep(self._timeFrame-(now - self._timeBook[-1])) # wait your turn... (maxTime - (now - oldest)) = time left to wait
			now = time.time() # look at watch, again...
			self._timeBook.insert(0, now) # add 'now' to the front of 'timeBook', pushing other times back
			if len(self._timeBook) > self._callLimit:self._timeBook.pop()  # remove the oldest time if 'timeBook' list is larger than 'callLimit'
