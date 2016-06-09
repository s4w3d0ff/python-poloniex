# Poloniex API wrapper for Python 2.7 and 3 - https://github.com/s4w3d0ff/python-poloniex
# BTC: 15D8VaZco22GTLVrFMAehXyif6EGf8GMYV
import sys, logging, json, time, calendar
import hmac, hashlib
import requests
# Tested on Python 2.7.6 & 3.4.3
if sys.version_info[0] == 3:
	from urllib.parse import urlencode
else:
	from urllib import urlencode
# Suppress the requests	module logging output
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

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
	def __init__(self, APIKey='', Secret='', timeout=3):
		"""
		self.APIKey = api key supplied by Poloniex
		self.Secret = secret hash supplied by Poloniex
		self.timeout = time in sec to wait for an api response (otherwise 'requests.exceptions.Timeout')
		
		
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
		
		self.marketTradeHist(pair, start, end) == json.loads(urlopen(Request('https://poloniex.com/public?'+urlencode({'command':'returnTradeHistory', 'currencyPair':<pair>, 'start':<start>, 'end':[end=time.time()]}))).read().decode(encoding='UTF-8'))		
		- returns trade public trade history for <pair> starting at <start> and ending at [end=time.time()]
		
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
		- toggles the 'autorenew' feature on a <orderId> 
		
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
		self.APIKey = APIKey
		self.Secret = Secret.encode('utf8')
		self.timeout = timeout
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
		self.marketTradeHist = lambda pair, start, end=time.time(): json.loads(urlopen(request('https://poloniex.com/public?'+urlencode({'command':'returnTradeHistory', 'currencyPair':str(pair), 'start':str(start), 'end':str(end)}))).read().decode(encoding='UTF-8'))		
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
		
	def api(self, command, args={}):
		"""
		Main Api Function
		- checks <command> is a vailid commmand
		- checks for APIKey and Secret if command is 'private'
		- returns 'False' if invalid command or if no APIKey or Secret is specified (if command is 'private')
		- sends url encoded string to API server, returns decoded json response
		- returns {"error":"<error message>"} if API error
		"""
		args['command'] = command
		global PUBLIC_COMMANDS
		global PRIVATE_COMMANDS
		if command in PRIVATE_COMMANDS:
			if len(self.APIKey) < 2 or len(self.Secret) < 2:
				print("An APIKey and Secret is needed!");return False
			url, args['nonce'] = ['https://poloniex.com/tradingApi', int(time.time()*42)]
			post_data = urlencode(args)
			sign = hmac.new(self.Secret, post_data.encode('utf-8'), hashlib.sha512).hexdigest()
			headers = {'Sign': sign, 'Key': self.APIKey}
			ret = requests.post('https://poloniex.com/tradingApi', data=args, headers=headers, timeout=self.timeout)
			return json.loads(ret.text)
					
		elif command in PUBLIC_COMMANDS:
			url = 'https://poloniex.com/public?'
			ret = requests.post(url + urlencode(args), timeout=self.timeout)
			return json.loads(ret.text)
			
		else:return False
