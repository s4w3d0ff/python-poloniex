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
from json import loads as _loads
from hmac import new as _new
from hashlib import sha512 as _sha512
# pip
from requests import post as _post
from requests import get as _get
# local
from .coach import (
    Coach, epoch2UTCstr, epoch2localstr,
    UTCstr2epoch, localstr2epoch, float2roundPercent,
    time, logging
)
# python 3 voodoo
try:
    from urllib.parse import urlencode as _urlencode
except ImportError:
    from urllib import urlencode as _urlencode

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
    'returnLendingHistory',
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
            self, Key=False, Secret=False,
            timeout=3, coach=False, loglevel=False, extend=False):
        """
        Key = str api key supplied by Poloniex
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
        self.logger = logging.getLogger(__name__)
        if loglevel:
            logging.getLogger("requests").setLevel(loglevel)
            logging.getLogger("urllib3").setLevel(loglevel)
            self.logger.setLevel(loglevel)
        # Call coach, set nonce
        self.apicoach, self.nonce = Coach(), int(time() * 1000)
        # Grab keys, set timeout, ditch coach?
        self.Key, self.Secret, self.timeout, self._coaching = \
            Key, Secret, timeout, coach
        # Set time labels
        self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.YEAR = \
            60, 60 * 60, 60 * 60 * 24, 60 * 60 * 24 * \
            7, 60 * 60 * 24 * 30, 60 * 60 * 24 * 365

        #   These namespaces are here because poloniex has overlapping
        # namespaces. There are 2 "returnTradeHistory" commands, one public and
        # one private. Currently if one were to try: polo('returnTradeHistory')
        # it would default to the private command and if no api key is defined a
        # 'ValueError' will be raise. The workaround is 'marketTradeHist'. It
        # returns the public data (bypassing the 'main' api call function). As
        # I continued to write this wrapper I found more 'practical' namespaces
        # for most of the api commands (at least at the time of writing). So I
        # added them here for those who wish to use them.
        if extend:
            # Public
            self.api = self.__call__
            self.marketTicker = self.returnTicker
            self.marketVolume = self.return24hVolume
            self.marketStatus = self.returnCurrencies
            self.marketLoans = self.returnLoanOrders
            self.marketOrders = self.returnOrderBook
            self.marketChart = self.returnChartData
            # Private
            self.myTradeHist = self.returnTradeHistory
            self.myBalances = self.returnBalances
            self.myAvailBalances = self.returnAvailableAccountBalances
            self.myMarginAccountSummary = self.returnMarginAccountSummary
            self.myMarginPosition = self.getMarginPosition
            self.myCompleteBalances = self.returnCompleteBalances
            self.myAddresses = self.returnDepositAddresses
            self.myOrders = self.returnOpenOrders
            self.myDepositsWithdraws = self.returnDepositsWithdrawals
            self.myTradeableBalances = self.returnTradableBalances
            self.myActiveLoans = self.returnActiveLoans
            self.myOpenLoanOrders = self.returnOpenLoanOffers
            self.myFeeInfo = self.returnFeeInfo
            self.myLendingHistory = self.returnLendingHistory
            self.orderTrades = self.returnOrderTrades
            self.createLoanOrder = self.createLoanOffer
            self.cancelLoanOrder = self.cancelLoanOffer

    # -----------------Meat and Potatos---------------------------------------
    def __call__(self, command, args={}):
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
            self.apicoach.wait()

        # pass the command
        args['command'] = command

        # private?
        if command in PRIVATE_COMMANDS:
            # check for keys
            if not self.Key or not self.Secret:
                raise ValueError("A Key and Secret needed!")
            # set nonce
            args['nonce'] = self.nonce

            try:
                # encode arguments for url
                postData = _urlencode(args)
                # sign postData with our Secret
                sign = _new(
                    self.Secret.encode('utf-8'),
                    postData.encode('utf-8'),
                    _sha512)
                # post request
                ret = _post(
                    'https://poloniex.com/tradingApi',
                    data=args,
                    headers={
                        'Sign': sign.hexdigest(),
                        'Key': self.Key
                    },
                    timeout=self.timeout)
            except Exception as e:
                raise e
            finally:
                # increment nonce(no matter what)
                self.nonce += 1
            # return decoded json
            try:
                return _loads(ret.text, parse_float=unicode)
            except NameError:
                return _loads(ret.text, parse_float=str)

        # public?
        elif command in PUBLIC_COMMANDS:
            try:
                ret = _get(
                    'https://poloniex.com/public?' + _urlencode(args),
                    timeout=self.timeout)
            except Exception as e:
                raise e
            try:
                return _loads(ret.text, parse_float=unicode)
            except NameError:
                return _loads(ret.text, parse_float=str)
        else:
            raise ValueError("Invalid Command!")

    # --PUBLIC COMMANDS-------------------------------------------------------
    def returnTicker(self):
        """ Returns the ticker for all markets """
        return self.__call__('returnTicker')

    def return24hVolume(self):
        """ Returns the volume data for all markets """
        return self.__call__('return24hVolume')

    def returnCurrencies(self):
        """ Returns additional market info for all markets """
        return self.__call__('returnCurrencies')

    def returnLoanOrders(self, coin):
        """ Returns loan order book for <coin> """
        return self.__call__('returnLoanOrders', {
                             'currency': str(coin).upper()})

    def returnOrderBook(self, pair='all', depth=20):
        """
        Returns orderbook for [pair='all']
        at a depth of [depth=20] orders
        """
        return self.__call__('returnOrderBook', {
            'currencyPair': str(pair).upper(),
            'depth': str(depth)
        })

    def returnChartData(self, pair, period=False, start=False, end=False):
        """
        Returns chart data for <pair> with a candle period of
        [period=self.DAY] starting from [start=time()-self.YEAR]
        and ending at [end=time()]
        """
        if not period:
            period = self.DAY
        if not start:
            start = time() - (self.MONTH * 2)
        if not end:
            end = time()
        return self.__call__('returnChartData', {
            'currencyPair': str(pair).upper(),
            'period': str(period),
            'start': str(start),
            'end': str(end)
        })

    def marketTradeHist(self, pair, start=False, end=False):
        """
        Returns public trade history for <pair>
        starting at <start> and ending at [end=time()]
        """
        if self._coaching:
            self.apicoach.wait()
        if not start:
            start = time() - self.HOUR
        if not end:
            end = time()
        try:
            ret = _get(
                'https://poloniex.com/public?' + _urlencode({
                    'command': 'returnTradeHistory',
                    'currencyPair': str(pair).upper(),
                    'start': str(start),
                    'end': str(end)
                }),
                timeout=self.timeout)
        except Exception as e:
            raise e
        try:
            return _loads(ret.text, parse_float=unicode)
        except NameError:
            return _loads(ret.text, parse_float=str)

    # --PRIVATE COMMANDS------------------------------------------------------
    def returnTradeHistory(self, pair):
        """ Returns private trade history for <pair> """
        return self.__call__('returnTradeHistory', {
                             'currencyPair': str(pair).upper()})

    def returnBalances(self):
        """ Returns coin balances """
        return self.__call__('returnBalances')

    def returnAvailableAccountBalances(self):
        """ Returns available account balances """
        return self.__call__('returnAvailableAccountBalances')

    def returnMarginAccountSummary(self):
        """ Returns margin account summary """
        return self.__call__('returnMarginAccountSummary')

    def getMarginPosition(self, pair='all'):
        """ Returns margin position for [pair='all'] """
        return self.__call__('getMarginPosition', {
                             'currencyPair': str(pair).upper()})

    def returnCompleteBalances(self, account='all'):
        """ Returns complete balances """
        return self.__call__('returnCompleteBalances',
                             {'account': str(account)})

    def returnDepositAddresses(self):
        """ Returns deposit addresses """
        return self.__call__('returnDepositAddresses')

    def returnOpenOrders(self, pair='all'):
        """ Returns your open orders for [pair='all'] """
        return self.__call__('returnOpenOrders', {
                             'currencyPair': str(pair).upper()})

    def returnDepositsWithdrawals(self, start=False, end=False):
        """ Returns deposit/withdraw history """
        if not start:
            start = time() - self.MONTH
        if not end:
            end = time()
        args = {'start': str(start), 'end': str(end)}
        return self.__call__('returnDepositsWithdrawals', args)

    def returnTradableBalances(self):
        """ Returns tradable balances """
        return self.__call__('returnTradableBalances')

    def returnActiveLoans(self):
        """ Returns active loans """
        return self.__call__('returnActiveLoans')

    def returnOpenLoanOffers(self):
        """ Returns open loan offers """
        return self.__call__('returnOpenLoanOffers')

    def returnFeeInfo(self):
        """ Returns current trading fees and trailing 30-day volume in BTC """
        return self.__call__('returnFeeInfo')

    def returnLendingHistory(self, start=False, end=False, limit=False):
        if not start:
            start = time() - self.MONTH
        if not end:
            end = time()
        args = {'start': str(start), 'end': str(end)}
        if limit:
            args['limit'] = str(limit)
        return self.__call__('returnLendingHistory', args)

    def returnOrderTrades(self, orderId):
        """ Returns any trades made from <orderId> """
        return self.__call__('returnOrderTrades', {
                             'orderNumber': str(orderId)})

    def createLoanOffer(self, coin, amount, rate, autoRenew=0, duration=2):
        """ Creates a loan offer for <coin> for <amount> at <rate> """
        return self.__call__('createLoanOffer', {
            'currency': str(coin).upper(),
            'amount': str(amount),
            'duration': str(duration),
            'autoRenew': str(autoRenew),
            'lendingRate': str(rate)
        })

    def cancelLoanOffer(self, orderId):
        """ Cancels the loan offer with <orderId> """
        return self.__call__('cancelLoanOffer', {'orderNumber': str(orderId)})

    def toggleAutoRenew(self, orderId):
        """ Toggles the 'autorenew' feature on loan <orderId> """
        return self.__call__('toggleAutoRenew', {'orderNumber': str(orderId)})

    def closeMarginPosition(self, pair):
        """ Closes the margin position on <pair> """
        return self.__call__('closeMarginPosition', {
                             'currencyPair': str(pair).upper()})

    def marginBuy(self, pair, rate, amount, lendingRate=2):
        """ Creates <pair> margin buy order at <rate> for <amount> """
        return self.__call__('marginBuy', {
            'currencyPair': str(pair).upper(),
            'rate': str(rate),
            'amount': str(amount),
            'lendingRate': str(lendingRate)
        })

    def marginSell(self, pair, rate, amount, lendingRate=2):
        """ Creates <pair> margin sell order at <rate> for <amount> """
        return self.__call__('marginSell', {
            'currencyPair': str(pair).upper(),
            'rate': str(rate),
            'amount': str(amount),
            'lendingRate': str(lendingRate)
        })

    def buy(self, pair, rate, amount, orderType=False):
        """ Creates buy order for <pair> at <rate> for
            <amount> with optional orderType """

        req = {
            'currencyPair': str(pair).upper(),
            'rate': str(rate),
            'amount': str(amount),
        }

        # order type specified?
        if orderType:
            possTypes = ['fillOrKill', 'immediateOrCancel', 'postOnly']
            # check type
            if not orderType in possTypes:
                raise ValueError('Invalid orderType')
            req[orderType] = 1

        return self.__call__('buy', req)

    def sell(self, pair, rate, amount, orderType=False):
        """ Creates sell order for <pair> at <rate> for
            <amount> with optional orderType """

        req = {
            'currencyPair': str(pair).upper(),
            'rate': str(rate),
            'amount': str(amount),
        }

        # order type specified?
        if orderType:
            possTypes = ['fillOrKill', 'immediateOrCancel', 'postOnly']
            # check type
            if not orderType in possTypes:
                raise ValueError('Invalid orderType')
            req[orderType] = 1

        return self.__call__('sell', req)

    def cancelOrder(self, orderId):
        """ Cancels order <orderId> """
        return self.__call__('cancelOrder', {'orderNumber': str(orderId)})

    def moveOrder(self, orderId, rate, amount, orderType=False):
        """ Moves an order by <orderId> to <rate> for <amount> """

        req = {
            'orderNumber': str(orderId),
            'rate': str(rate),
            'amount': str(amount)
        }

        # order type specified?
        if orderType:
            possTypes = ['immediateOrCancel', 'postOnly']
            # check type
            if not orderType in possTypes:
                raise ValueError('Invalid orderType')
            req[orderType] = 1

        return self.__call__('moveOrder', req)

    def withdraw(self, coin, amount, address, paymentId=False):
        """ Withdraws <coin> <amount> to <address> """
        req = {
            'currency': str(coin).upper(),
            'amount': str(amount),
            'address': str(address)
        }
        if paymentId:
            req['paymentId'] = str(paymentId)
        return self.__call__('withdraw', req)

    def transferBalance(self, coin, amount, fromac, toac):
        """
        Transfers coins between accounts (exchange, margin, lending)
        - moves <coin> <amount> from <fromac> to <toac>
        """
        return self.__call__('transferBalance', {
            'currency': str(coin).upper(),
            'amount': str(amount),
            'fromAccount': str(fromac),
            'toAccount': str(toac)
        })
