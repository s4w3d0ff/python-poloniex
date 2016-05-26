import sys, json, time, calendar
import hmac, hashlib
# Tested on Python 2.7.6 & 3.4.3
if sys.version_info[0] == 3:
	from urllib.request import Request, urlopen
	from urllib.parse import urlencode
else:
	from urllib2 import Request, urlopen
	from urllib import urlencode
# Possible Commands
PUBLIC_COMMANDS = ['returnTicker', 'return24hVolume', 'returnOrderBook', 'returnTradeHistory', 'returnChartData', 'returnCurrencies', 'returnLoanOrders'] 
PRIVATE_COMMANDS = ['returnBalances', 'returnCompleteBalances', 'returnDepositAddresses', 'generateNewAddress', 'returnDepositsWithdrawals', 'returnOpenOrders', 'returnTradeHistory', 'returnAvailableAccountBalances', 'returnTradableBalances', 'returnOpenLoanOffers', 'returnActiveLoans', 'createLoanOffer', 'cancelLoanOffer', 'toggleAutoRenew', 'buy', 'sell', 'cancelOrder', 'moveOrder', 'withdraw', 'transferBalance', 'returnMarginAccountSummary', 'marginBuy', 'marginSell', 'getMarginPosition', 'closeMarginPosition']
class Poloniex(object):
	"""The Poloniex Object!"""
	def __init__(self, APIKey='', Secret=''):
		"""
		self.APIKey = Your api key supplied by Poloniex
		self.Secret = Your secret hash supplied by Poloniex
		
		# Time Placeholders (MONTH = 30*DAYS):
		self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.YEAR
		
		---Legend:<requiredArg>[optionalArg=defaultValue]---
		
		# Time Conversions:
		self.epoch2UTCstr = takes epoch [timestamp=time.time()], returns UTC formated [fmat="%Y-%m-%d %H:%M:%S"] string
		self.UTCstr2epoch = takes UTC date string [datestr=self.epoch2UTCstr()] formated as [fmat="%Y-%m-%d %H:%M:%S"], returns epoch
		self.epoch2localstr = takes epoch [timestamp=time.time()], returns localtimezone formated [fmat="%Y-%m-%d %H:%M:%S"] string
		self.localstr2epoch = takes localtimezone date string [datestr=self.epoch2UTCstr()] formated as [fmat="%Y-%m-%d %H:%M:%S"], returns epoch
		# Conversions
		self.float2roundPercent = takes <float>, returns percent(*100) rounded to the [decimalP=2] decimal place as a string
		
		#PUBLIC COMMANDS
		self.marketTicker = returns the ticker for all markets = self.api('returnTicker')
		self.marketVolume = returns the volume data for all markets = self.api('return24hVolume')
		self.marketStatus = returns additional market info for all markets = self.api('returnCurrencies')
		self.marketLoans = returns open loan orders for <coin> = self.api('returnLoanOrders',{'currency':<coin>})
		self.marketOrders = returns orderbook for [pair='all'] at a depth of [depth=20] orders = self.api('returnOrderBook', {'currencyPair':[pair='all'], 'depth':[depth=20]})
		self.marketChart = returns chart data for <pair> with a candle period of [period=self.DAY] starting from [start=time.time()-self.YEAR] and ending at [end=time.time()] = self.api('returnChartData', {'currencyPair':<pair>, 'period':[period=self.DAY], 'start':[start=time.time()-self.YEAR], 'end':[end=time.time()]})
		self.marketTradeHist = returns trade public trade history for <pair> starting at <start> and ending at [end=time.time()] = json.loads(urlopen(Request('https://poloniex.com/public?'+urlencode({'command':'returnTradeHistory', 'currencyPair':<pair>, 'start':<start>, 'end':[end=time.time()]}))).read().decode(encoding='UTF-8'))		
		
		#PRIVATE COMMANDS
		self.myTradeHist = returns your private trade history for <pair> = self.api('returnTradeHistory',{'currencyPair':<pair>})
		self.myAvailBalances = returns your available account balances = self.api('returnAvailableAccountBalances')
		self.myMarginAccountSummary = returns your margin account summary = self.api('returnMarginAccountSummary')
		self.myMarginPosition = returns your margin position for [pair='all'] = self.api('getMarginPosition',{'currencyPair':[pair='all']})
		self.myCompleteBalances = returns your complete balances = self.api('returnCompleteBalances')
		self.myAddresses = returns your deposit addresses = self.api('returnDepositAddresses')
		self.myOrders = returns your open orders for [pair='all'] = self.api('returnOpenOrders',{'currencyPair':[pair='all']})
		self.myDepositsWithdraws = returns your deposit/withdraw history = self.api('returnDepositsWithdrawals')
		self.myTradeableBalances = returns your tradable balances = self.api('returnTradableBalances')
		self.myActiveLoans = returns your active loans = self.api('returnActiveLoans')
		self.myOpenLoanOrders = returns your open loan offers = self.api('returnOpenLoanOffers')
		## Trading functions ##
		self.createLoanOrder = creates a loan offer for <coin> for <amount> at <rate> = self.api('createLoanOffer', {'currency' :<coin>, 'amount':<amount>, 'duration':2, 'autoRenew':0, 'lendingRate':<rate>})
		self.cancelLoanOrder = cancels the loan offer with <orderId> self.api('cancelLoanOffer', {'orderNumber':<orderId>})
		self.toggleAutoRenew = toggles the 'autorenew' feature on a <orderId> = self.api('toggleAutoRenew', {'orderNumber':<orderId>})
		self.closeMarginPosition = closes the margin position on <pair> = self.api('closeMarginPosition',{'currencyPair':<pair>})
		self.marginBuy = creates a margin buy order for <pair> at <rate> for <amount> with [lendingRate=2]% = self.api('marginBuy', {'currencyPair':<pair>, 'rate':<rate>, 'amount':<amount>, 'lendingRate':[lendingRate=2]})
		self.marginSell= creates a margin sell order for <pair> at <rate> for <amount> with [lendingRate=2]% = self.api('marginSell', {'currencyPair':<pair>, 'rate':<rate>, 'amount':<amount>, 'lendingRate':[lendingRate=2]})
		self.buy = creates buy order for <pair> at <rate> for <amount> = self.api('buy', {'currencyPair':<pair>, 'rate':<rate>, 'amount':<amount>})
		self.sell = creates sell order for <pair> at <rate> for <amount> = self.api('sell', {'currencyPair':<pair>, 'rate':<rate>, 'amount':<amount>})
		self.cancelOrder = cancels order <orderId> = self.api('cancelOrder', {'orderNumber':<orderId>})
		self.moveOrder = moves order <orderId> to <rate> for <amount> = self.api('moveOrder', {'orderNumber':<orderId>, 'rate':<rate>, 'amount':<amount>})
		self.withdraw = withdraws <coin> <amount> to <address> = self.api('withdraw', {'currency':<coin>, 'amount':<amount>, 'address':<address>})
		self.transferBalance = moves <coin> <amount> from <fromac> to <toac> = self.api('transferBalance', {'currency':<coin>, 'amount':<amount>, 'fromAccount':<fromac>, 'toAccount':<toac>})
		"""
		self.APIKey = APIKey
		self.Secret = Secret.encode('utf8')
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
		self.marketTradeHist = lambda pair, start, end=time.time(): json.loads(urlopen(Request('https://poloniex.com/public?'+urlencode({'command':'returnTradeHistory', 'currencyPair':str(pair), 'start':str(start), 'end':str(end)}))).read().decode(encoding='UTF-8'))		
		#PRIVATE COMMANDS
		self.myTradeHist = lambda pair: self.api('returnTradeHistory',{'currencyPair':str(pair)})
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
		self.transferBalance = lambda coin, amount, fromac, toac: self.api('transferBalance', {'currency':str(coin), 'amount':str(amount), 'fromAccount':str(fromac), 'toAccount':str(toac)})
		
	def api(self, command, args={}):
		"""
		Main Api Function
		- checks to make sure <command> is a vailid commmand
		- checks for APIKey and Secret if command is 'private'
		- returns 'False' if invalid command or if no APIKey or Secret is specified (if command is 'private')
		- sends url encoded string to API server, decodes json response and returns dict
		- returns {"error":"<error message>"} if API error
		"""
		args['command'] = command
		if command in PRIVATE_COMMANDS:
			if len(self.APIKey) < 2 or len(self.Secret) < 2:
				print("An APIKey and Secret is needed!");return False
			url, args['nonce'] = ['https://poloniex.com/tradingApi', int(time.time()*42)]
			post_data = urlencode(args).encode('utf8')
			sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
			headers = {'Sign': sign, 'Key': self.APIKey}
			ret = urlopen(Request(url, post_data, headers))
			return json.loads(ret.read().decode(encoding='UTF-8'))
		elif command in PUBLIC_COMMANDS:
			url = 'https://poloniex.com/public?'
			ret = urlopen(Request(url + urlencode(args)))
			return json.loads(ret.read().decode(encoding='UTF-8'))
		else:return False
