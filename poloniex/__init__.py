# Poloniex API wrapper tested on Python 2.7.6 & 3.4.3
# https://github.com/s4w3d0ff/python-poloniex
# BTC: 15D8VaZco22GTLVrFMAehXyif6EGf8GMYV
# TODO:
#   [x] PEP8
#   [ ] Add better logger access
#   [ ] Find out if request module has the equivalent to urlencode
#   [ ] Add Push Api application wrapper
#   [ ] Convert docstrings to sphinx
#
#    Copyright (C) 2016  https://github.com/s4w3d0ff
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import sys
import time
import calendar
import logging
import json
import hmac
import hashlib
# pip
import requests

from coach import Coach

if sys.version_info[0] is 3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode

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
    def __init__(
            self, APIKey=False, Secret=False,
            timeout=3, coach=False, loglevel=logging.WARNING):
        """
        APIKey = str api key supplied by Poloniex
        Secret = str secret hash supplied by Poloniex
        timeout = int time in sec to wait for an api response
            (otherwise 'requests.exceptions.Timeout' is raised)
        coach = bool to indicate if the api coach should be used
        loglevel = logging level object to set the module at
            (changes the requests module as well)

        self.apiCoach = object that regulates spacing between api calls

        # Time Placeholders # (MONTH == 30*DAYS)

        self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.YEAR
        """
        # Set wrapper logging level
        logging.basicConfig(
                format='[%(asctime)s] %(message)s',
                datefmt="%H:%M:%S",
                level=loglevel)
        # Suppress the requests	module logging output
        logging.getLogger("requests").setLevel(loglevel)
        logging.getLogger("urllib3").setLevel(loglevel)
        # Call coach, set nonce
        self.apiCoach, self.nonce = [Coach(), int(time.time()*1000)]
        # Grab keys, set timeout, ditch coach?
        self.APIKey, self.Secret, self.timeout, self._coaching = \
            [APIKey, Secret, timeout, coach]
        # Set time labels
        self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.YEAR = \
            [60, 60*60, 60*60*24, 60*60*24*7, 60*60*24*30, 60*60*24*365]

    # -----------------Meat and Potatos---------------------------------------
    def api(self, command, args={}):
        """
        Main Api Function
        - encodes and sends <command> with optional [args] to Poloniex api
        - raises 'ValueError' if an api key or secret is missing
            (and the command is 'private'), or if the <command> is not valid
        - returns decoded json api message
        """
        global PUBLIC_COMMANDS, PRIVATE_COMMANDS

        # check in with the coach
        if self._coaching:
            self.apiCoach.wait()

        # pass the command
        args['command'] = command

        # private?
        if command in PRIVATE_COMMANDS:
            # check for keys
            if not self.APIKey or not self.Secret:
                raise ValueError("APIKey and Secret needed!")
            # set nonce
            args['nonce'] = self.nonce

            try:
                # encode arguments for url
                postData = urlencode(args)
                # sign postData with our Secret
                sign = hmac.new(
                        self.Secret.encode('utf-8'),
                        postData.encode('utf-8'),
                        hashlib.sha512)
                # post request
                ret = requests.post(
                        'https://poloniex.com/tradingApi',
                        data=args,
                        headers={
                            'Sign': sign.hexdigest(),
                            'Key': self.APIKey
                            },
                        timeout=self.timeout)
                # return decoded json
                return json.loads(ret.text)

            except Exception as e:
                raise e

            finally:
                # increment nonce(no matter what)
                self.nonce += 1

        # public?
        elif command in PUBLIC_COMMANDS:
            try:
                ret = requests.post(
                        'https://poloniex.com/public?' + urlencode(args),
                        timeout=self.timeout)
                return json.loads(ret.text)
            except Exception as e:
                raise e
        else:
            raise ValueError("Invalid Command!")

    # Convertions
    def epoch2UTCstr(self, timestamp=time.time(), fmat="%Y-%m-%d %H:%M:%S"):
        """
        - takes epoch timestamp
        - returns UTC formated string
        """
        return time.strftime(fmat, time.gmtime(timestamp))

    def UTCstr2epoch(self, datestr=False, fmat="%Y-%m-%d %H:%M:%S"):
        """
        - takes UTC date string
        - returns epoch
        """
        if not datestr:
            datestr = self.epoch2UTCstr()
        return calendar.timegm(time.strptime(datestr, fmat))

    def epoch2localstr(self, timestamp=time.time(), fmat="%Y-%m-%d %H:%M:%S"):
        """
        - takes epoch timestamp
        - returns localtimezone formated string
        """
        return time.strftime(fmat, time.localtime(timestamp))

    def localstr2epoch(self, datestr=False, fmat="%Y-%m-%d %H:%M:%S"):
        """
        - takes localtimezone date string,
        - returns epoch
        """
        if not datestr:
            datestr = self.epoch2UTCstr()
        return time.mktime(time.strptime(datestr, fmat))

    def float2roundPercent(self, floatN, decimalP=2):
        """
        - takes float
        - returns percent(*100) rounded to the Nth decimal place as a string
        """
        return str(round(float(floatN)*100, decimalP))+"%"

    # --PUBLIC COMMANDS-------------------------------------------------------
    def marketTicker(self):
        """ Returns the ticker for all markets """
        return self.api('returnTicker')

    def marketVolume(self):
        """ Returns the volume data for all markets """
        return self.api('return24hVolume')

    def marketStatus(self):
        """ Returns additional market info for all markets """
        return self.api('returnCurrencies')

    def marketLoans(self, coin):
        """ Returns loan order book for <coin> """
        return self.api('returnLoanOrders', {'currency': str(coin)})

    def marketOrders(self, pair='all', depth=20):
        """
        Returns orderbook for [pair='all']
        at a depth of [depth=20] orders
        """
        return self.api('returnOrderBook', {
                    'currencyPair': str(pair),
                    'depth': str(depth)
                    })

    def marketChart(self, pair, period=False, start=False, end=time.time()):
        """
        Returns chart data for <pair> with a candle period of
        [period=self.DAY] starting from [start=time.time()-self.YEAR]
        and ending at [end=time.time()]
        """
        if not period:
            period = self.DAY
        if not start:
            start = time.time()-(self.MONTH*2)
        return self.api('returnChartData', {
                    'currencyPair': str(pair),
                    'period': str(period),
                    'start': str(start),
                    'end': str(end)
                    })

    def marketTradeHist(self, pair, start=False, end=time.time()):
        """
        Returns public trade history for <pair>
        starting at <start> and ending at [end=time.time()]
        """
        if self._coaching:
            self.apiCoach.wait()
        if not start:
            start = time.time()-self.HOUR
        try:
            ret = requests.post(
                    'https://poloniex.com/public?'+urlencode({
                        'command': 'returnTradeHistory',
                        'currencyPair': str(pair),
                        'start': str(start),
                        'end': str(end)
                        }),
                    timeout=self.timeout)
            return json.loads(ret.text)
        except Exception as e:
            raise e

    # --PRIVATE COMMANDS------------------------------------------------------
    def myTradeHist(self, pair):
        """ Returns private trade history for <pair> """
        return self.api('returnTradeHistory', {'currencyPair': str(pair)})

    def myBalances(self):
        """ Returns coin balances """
        return self.api('returnBalances')

    def myAvailBalances(self):
        """ Returns available account balances """
        return self.api('returnAvailableAccountBalances')

    def myMarginAccountSummary(self):
        """ Returns margin account summary """
        return self.api('returnMarginAccountSummary')

    def myMarginPosition(self, pair='all'):
        """ Returns margin position for [pair='all'] """
        return self.api('getMarginPosition', {'currencyPair': str(pair)})

    def myCompleteBalances(self):
        """ Returns complete balances """
        return self.api('returnCompleteBalances')

    def myAddresses(self):
        """ Returns deposit addresses """
        return self.api('returnDepositAddresses')

    def myOrders(self, pair='all'):
        """ Returns your open orders for [pair='all'] """
        return self.api('returnOpenOrders', {'currencyPair': str(pair)})

    def myDepositsWithdraws(self):
        """ Returns deposit/withdraw history """
        return self.api('returnDepositsWithdrawals')

    def myTradeableBalances(self):
        """ Returns tradable balances """
        return self.api('returnTradableBalances')

    def myActiveLoans(self):
        """ Returns active loans """
        return self.api('returnActiveLoans')

    def myOpenLoanOrders(self):
        """ Returns open loan offers """
        return self.api('returnOpenLoanOffers')

    # --Trading functions-- #
    def orderTrades(self, orderId):
        """ Returns any trades made from <orderId> """
        return self.api('returnOrderTrades', {'orderNumber': str(orderId)})

    def createLoanOrder(self, coin, amount, rate):
        """ Creates a loan offer for <coin> for <amount> at <rate> """
        return self.api('createLoanOffer', {
                    'currency': str(coin),
                    'amount': str(amount),
                    'duration': str(2),
                    'autoRenew': str(0),
                    'lendingRate': str(rate)
                    })

    def cancelLoanOrder(self, orderId):
        """ Cancels the loan offer with <orderId> """
        return self.api('cancelLoanOffer', {'orderNumber': str(orderId)})

    def toggleAutoRenew(self, orderId):
        """ Toggles the 'autorenew' feature on loan <orderId> """
        return self.api('toggleAutoRenew', {'orderNumber': str(orderId)})

    def closeMarginPosition(self, pair):
        """ Closes the margin position on <pair> """
        return self.api('closeMarginPosition', {'currencyPair': str(pair)})

    def marginBuy(self, pair, rate, amount, lendingRate=2):
        """ Creates <pair> margin buy order at <rate> for <amount> """
        return self.api('marginBuy', {
                    'currencyPair': str(pair),
                    'rate': str(rate),
                    'amount': str(amount),
                    'lendingRate': str(lendingRate)
                    })

    def marginSell(self, pair, rate, amount, lendingRate=2):
        """ Creates <pair> margin sell order at <rate> for <amount> """
        return self.api('marginSell', {
                    'currencyPair': str(pair),
                    'rate': str(rate),
                    'amount': str(amount),
                    'lendingRate': str(lendingRate)
                    })

    def buy(self, pair, rate, amount):
        """ Creates buy order for <pair> at <rate> for <amount> """
        return self.api('buy', {
                    'currencyPair': str(pair),
                    'rate': str(rate),
                    'amount': str(amount)
                    })

    def sell(self, pair, rate, amount):
        """ Creates sell order for <pair> at <rate> for <amount> """
        return self.api('sell', {
                    'currencyPair': str(pair),
                    'rate': str(rate),
                    'amount': str(amount)
                    })

    def cancelOrder(self, orderId):
        """ Cancels order <orderId> """
        return self.api('cancelOrder', {'orderNumber': str(orderId)})

    def moveOrder(self, orderId, rate, amount):
        """ Moves an order by <orderId> to <rate> for <amount> """
        return self.api('moveOrder', {
                    'orderNumber': str(orderId),
                    'rate': str(rate),
                    'amount': str(amount)
                    })

    def withdraw(self, coin, amount, address):
        """ Withdraws <coin> <amount> to <address> """
        return self.api('withdraw', {
                    'currency': str(coin),
                    'amount': str(amount),
                    'address': str(address)
                    })

    def returnFeeInfo(self):
        """ Returns current trading fees and trailing 30-day volume in BTC """
        return self.api('returnFeeInfo')

    def transferBalance(self, coin, amount, fromac, toac):
        """
        Transfers coins between accounts (exchange, margin, lending)
        - moves <coin> <amount> from <fromac> to <toac>
        """
        return self.api('transferBalance', {
                    'currency': str(coin),
                    'amount': str(amount),
                    'fromAccount': str(fromac),
                    'toAccount': str(toac)
                    })
