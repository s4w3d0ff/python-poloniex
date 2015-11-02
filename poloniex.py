import json
import time
import hmac,hashlib
import sys
# Tested on Python 2.7.6 & 3.4.3
if sys.version_info[0] == 3:
	from urllib.request import Request, urlopen
	from urllib.parse import urlencode
else:
	from urllib import urlencode
	from urllib2 import Request, urlopen
# Possible Commands
PUBLIC_COMMANDS = ['returnTicker','return24Volume','returnOrderBook','returnTradeHistory','returnChartData','returnCurrencies','returnLoanOrders'] 
PRIVATE_COMMANDS = ['returnBalances','returnCompleteBalances','returnDepositAddresses','generateNewAddress','returnDepositsWithdrawals','returnOpenOrders','returnTradeHistory','buy','sell','cancelOrder','moveOrder','withdraw','returnAvailableAccountBalances','returnTradableBalances','transferBalance','returnMarginAccountSummary','marginBuy','marginSell','getMarginPosition','closeMarginPosition','createLoanOffer','cancelLoanOffer','returnOpenLoanOffers','returnActiveLoans','toggleAutoRenew']

class Poloniex:
	def __init__(self, APIKey=False, Secret=False):
		self.APIKey = APIKey
		self.Secret = Secret
		timestamp_str = lambda timestamp=time.time(), format="%Y-%m-%d %H:%M:%S": datetime.fromtimestamp(timestamp).strftime(format)
		str_timestamp = lambda datestr=timestamp_str() , format="%Y-%m-%d %H:%M:%S": int(time.mktime(time.strptime(datestr, format)))
		
	def api(self, command, args={}):
		"""
		returns 'False' if invalid command or if no APIKey or Secret is specified (if command is "private")
		returns {"error":"<error message>"} if API error
		"""
		args['command'] = command
		if command in PUBLIC_COMMANDS:
			url = 'https://poloniex.com/public?'
			if not args:
				ret = urlopen(Request(url + command))
				return json.loads(ret.read().decode(encoding='UTF-8'))
			else:
				ret = urlopen(Request(url + urlencode(args)))
				return json.loads(ret.read().decode(encoding='UTF-8'))
		elif command in PRIVATE_COMMANDS:
			if not self.APIKey or self.Secret:
				print("An APIKey and Secret is needed!")
				return False
			url = 'https://poloniex.com/tradingApi'
			args['nonce'] = int(time.time()*42)
			post_data = urlencode(args)
			sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
			headers = {'Sign': sign, 'Key': self.APIKey}
			ret = urlopen(Request(url, post_data, headers))
			return json.loads(ret.read().decode(encoding='UTF-8'))
		else:return False
