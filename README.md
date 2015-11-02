# poloapi

A Python Poloniex.com API wrapper - Tested on Python 2.7.6 & 3.4.3 

Based off of a wrapper written by 'oipminer': [http://pastebin.com/8fBVpjaj]

##Updates:
-ApiKey and Secret are optional if used for just public commands.

-Returns 'False' if the command supplied does not exist (this helps on Poloniex API bandwith) .

##Examples:
Public Commands (APIKey and Secret optional):

```python
import poloniex
polo = poloniex.Poloniex()
    
# get ticker
ticker = polo.api('returnTicker')
print(ticker['CGA'])
    
# get CGA orderbook
ordersCGA = polo.api('returnOrderBook',{'currency':'CGA'})
print(ordersCGA)
```

Private Commands (APIKey and Secret required):
```python
import poloniex
polo = poloniex.poloniex('yourApiKeyHere','yourSecretKeyHere123')
    
# Get all your balances
balance = polo.api('returnBalances')
print("I have %s CGA!" % balance['CGA'])
    
# Make new CGA deposit address
newDepositAddress = polo.api('generateNewAddress',{'currency':'CGA'})
print(newDepositAddress)
    
# Sell all your CGA :D (CAUTION!!!1)
print(polo.api('sell', {'currencyPair': 'BTC_CGA', "rate": 0.003 , "amount": balance['CGA'] }))
```

(PUSH API is currently not supported, if you would like to contribute in the development of this repository please fork and make a pull request.)
