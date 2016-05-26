#**An API wrapper for Poloniex.com written in Python**
#####poloniex.py - _Tested on Python 2.7.6 & 3.4.3_
Based off of a wrapper written by 'oipminer': [http://pastebin.com/8fBVpjaj]

###Features:
- ApiKey and Secret are optional if used for just public commands.
- Returns `False` if the command supplied does not exist (this helps on bandwith when testing) .
- Api Commands have been 'mapped' into lambdas for your conveniance.

###Examples:
#### **Basic Public Setup (no ApiKey/Secret):**
```python
import poloniex
polo = poloniex.Poloniex()
```
##### Get Ticker
```python
ticker = polo.api('returnTicker')
print(ticker['BTC_CGA'])
# or
ticker = polo.marketTicker()
print(ticker['BTC_CGA'])
```
##### Get Market Loan Orders
```python
BTCloanOrders = polo.api('returnLoanOrders',{'currency':'BTC'})
print(BTCloanOrders)
# or 
BTCloanOrders = polo.marketLoans('BTC')
print(BTCloanOrders)
```

#### **Basic Private Setup (ApiKey/Secret required):**
```python
import poloniex

polo = poloniex.Poloniex('yourApiKeyHere','yourSecretKeyHere123')
# or
polo.APIKey = 'yourApiKeyHere'
polo.Secret = 'yourSecretKeyHere123'
```
##### Get all your balances
```python
balance = polo.api('returnBalances')
print("I have %s CGA!" % balance['CGA'])
# or
balance = polo.myBalances()
print("I have %s BTC!" % balance['BTC'])
```
##### Make new CGA deposit address
```python
print(polo.api('generateNewAddress',{'currency':'CGA'}))
# or
print(polo.generateNewAddress('CGA'))
```
##### Sell 10 CGA for 0.003 BTC
```python
print(polo.api('sell', {'currencyPair': 'BTC_CGA', 'rate': '0.003' , 'amount': '10' }))
# or
print(polo.sell('BTC_CGA', '0.003', '10'))
```

An example of a WAMP application using the websocket push API can be found here: https://github.com/s4w3d0ff/python-poloniex/blob/master/examples/polocalbox.py

You like?
```
CGA: aZ1yHGx4nA64aWMDNQKXJrojso7gfQ1J5P
BTC: 15D8VaZco22GTLVrFMAehXyif6EGf8GMYV
LTC: LakbntAYrwpVSnLWj1fCLttVzpiDXDa5JV
DOGE: DAQjkQNbhpUoQw7KHAGkDYZ3yySKi751dd
```
