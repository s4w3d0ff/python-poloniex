# apipolo

**A Python Poloniex.com API wrapper** - Tested on Python 2.7.6 & 3.4.3

Based off of a wrapper written by 'oipminer': [http://pastebin.com/8fBVpjaj]

###Updates:
-ApiKey and Secret are optional if used for just public commands.

-Returns `False` if the command supplied does not exist (this helps on Poloniex API bandwith) .

###Examples:
Public Commands (APIKey and Secret optional):

```python
import poloniex

polo = poloniex.Poloniex()
    
# get ticker

ticker = polo.api('returnTicker')
print(ticker['CGA'])
# or
ticker = polo.marketTicker()
print(ticker['CGA'])

# get Loan Orders

BTCloanOrders = polo.api('returnLoanOrders',{'currency':'BTC'})
print(BTCloanOrders)
# or 
BTCloanOrders = polo.marketLoans('BTC')
print(BTCloanOrders)
```

Private Commands (APIKey and Secret required):
```python
import poloniex

polo = poloniex.Poloniex('yourApiKeyHere','yourSecretKeyHere123')
# or
polo.APIKey = 'yourApiKeyHere'
polo.Secret = 'yourSecretKeyHere123'

# Get all your balances

balance = polo.api('returnBalances')
print("I have %s CGA!" % balance['CGA'])
# or
balance = polo.myBalances()
print("I have %s BTC!" % balance['BTC'])

# Make new CGA deposit address

print(polo.api('generateNewAddress',{'currency':'CGA'}))
# or
print(polo.generateNewAddress('CGA'))

# Sell 10 CGA for 0.003 BTC

print(polo.api('sell', {'currencyPair': 'BTC_CGA', 'rate': 0.003 , 'amount': 10 }))
# or
print(polo.sell('BTC_CGA', 0.003, 10))
```

(PUSH API is currently not supported, if you would like to contribute in the development of this repository please fork and make a pull request.)
