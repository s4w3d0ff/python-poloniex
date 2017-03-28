# **An API wrapper for Poloniex.com written in Python**
##### _Tested on Python 2.7.12 & 3.5.2_
Inspired by [this](http://pastebin.com/8fBVpjaj) wrapper written by 'oipminer'

### Features:
- The first 2 args in the `poloniex.Poloniex` object (`Key` and `Secret`) are _optional_ when used for _public api commands_.
- Api commands have been 'mapped' into methods within the `Poloniex` class for your convenience.
- Raises `ValueError` if the command supplied does not exist __or__ if the api keys are not defined and attempting to access a private api command.
- The `poloniex.Poloniex(timeout=3)` attribute/arg adjusts the number of seconds to wait for a response from poloniex, else `requests.exceptions.Timeout` is raised.
- A call restrictor (`coach`) is enabled by default, limiting the api wrapper to 6 calls per second. If you wish, you can deactivate the coach using `Poloniex(coach=False)`.
- By default, json floats are parsed as strings (ints are ints), you can define `Poloniex(jsonNums=float)` to have _all numbers_ (floats _and_ ints) parsed as floats (or import and use `decimal.Decimal`).
- `poloniex.coach` and `poloniex.Poloniex` have self named loggers. You can define the log level of the `requests` module by defining `Poloniex(loglevel=logging.DEBUG)` (this also changes the log level of the `Poloniex` object).

## Install:
Python 2: 
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
### Basic Public Setup (no ApiKey/Secret):
```python
from poloniex import Poloniex
polo = Poloniex()
```
Ticker
```python
print(polo('returnTicker')['BTC_ETH'])
# or
print(polo.returnTicker()['BTC_ETH'])
```
Public trade history:
```python
print(polo.marketTradeHist('BTC_ETH'))
```

### Basic Private Setup (ApiKey/Secret required):
```python
import poloniex
polo = poloniex.Poloniex('your-Api-Key-Here-xxxx','yourSecretKeyHere123456789')
# or
polo.Key = 'your-Api-Key-Here-xxxx'
polo.Secret = 'yourSecretKeyHere123456789'
```
Get all your balances
```python
balance = polo.returnBalances()
print("I have %s ETH!" % balance['ETH'])
# or
balance = polo('returnBalances')
print("I have %s BTC!" % balance['BTC'])
```

**Examples of WAMP applications using the websocket push API can be found [here](https://github.com/s4w3d0ff/python-poloniex/tree/master/examples).**
