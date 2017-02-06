# **An API wrapper for Poloniex.com written in Python**
#####poloniex.py - _Tested on Python 2.7.12 & 3.5.2_
Inspired by [this](http://pastebin.com/8fBVpjaj) wrapper written by 'oipminer'

### Features:
- ApiKey and Secret are optional if used for just public commands.
- Api Commands have been 'mapped' into methods within the Poloniex class for your convenience.
- Raises `ValueError` if the command supplied does not exist or if the api keys are not defined
- The `poloniex.Poloniex()` object has an optional 'timeout' attribute/arg that adjusts the number of seconds to wait for a response from polo (default = 3 sec)
- Optional api 'coach' can restrict the amount of calls per sec, keeping your api calls (that aren't threaded) under the limit (6 calls per sec). Activate the coach using `poloniex.Poloniex(coach=True)` when creating the polo object or by defining `polo._coaching = True`.

## Install:Python 2: 
```
pip install git+https://github.com/s4w3d0ff/python-poloniex.git
```

Python 3: 
```
pip3 install git+https://github.com/s4w3d0ff/python-poloniex.git
```

## Uninstall:
Python 2: 
```
pip uninstall poloniex
```

Python 3: 
```
pip3 uninstall poloniex
```

## Usage:
#### **Basic Public Setup (no ApiKey/Secret):**
```python
from poloniex import Poloniex
polo = Poloniex()
```
##### Ticker
```python
print(polo('returnTicker')['BTC_ETH'])
# or
print(polo.returnTicker()['BTC_ETH'])
```
##### Public trade history:
```python
print(polo.marketTradeHist('BTC_ETH'))
```

#### **Basic Private Setup (ApiKey/Secret required):**
```python
import poloniex
polo = poloniex.Poloniex('your-Api-Key-Here-xxxx','yourSecretKeyHere123456789')
# or
polo.Key = 'your-Api-Key-Here-xxxx'
polo.Secret = 'yourSecretKeyHere123456789'
```
##### Get all your balances
```python
balance = polo.returnBalances()
print("I have %s ETH!" % balance['ETH'])
# or
balance = polo('returnBalances')
print("I have %s BTC!" % balance['BTC'])
```

**Examples of WAMP applications using the websocket push API can be found [here](https://github.com/s4w3d0ff/python-poloniex/tree/master/examples).**
