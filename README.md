![python](https://img.shields.io/badge/python-2.7%20%26%203-blue.svg) [![licence](https://img.shields.io/badge/licence-GPL%20v2-blue.svg)](https://github.com/s4w3d0ff/python-poloniex/blob/master/LICENSE)  
[![release](https://img.shields.io/github/release/s4w3d0ff/python-poloniex.svg) ![release build](https://travis-ci.org/s4w3d0ff/python-poloniex.svg?branch=v0.3.6)](https://github.com/s4w3d0ff/python-poloniex/releases)  
[![master](https://img.shields.io/badge/branch-master-blue.svg) ![master build](https://api.travis-ci.org/s4w3d0ff/python-poloniex.svg?branch=master)](https://github.com/s4w3d0ff/python-poloniex/tree/master)  
[![dev](https://img.shields.io/badge/branch-dev-blue.svg) ![dev build](https://api.travis-ci.org/s4w3d0ff/python-poloniex.svg?branch=dev)](https://github.com/s4w3d0ff/python-poloniex/tree/dev)  
Inspired by [this](http://pastebin.com/8fBVpjaj) wrapper written by 'oipminer'

## Install latest release:
Python 2:
```
pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.1.zip
```

Python 3:
```
pip3 install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.1.zip
```

### Features:
- The first 2 args in the `poloniex.Poloniex` object (`key` and `secret`) are _optional_ when used for _public api commands_.
- Api commands have been 'mapped' into methods within the `Poloniex` class for your convenience.
- Raises `poloniex.PoloniexError` if the command supplied does not exist, if the api keys are not defined and attempting to access a private api command, or if Poloniex.com returns an api error.
- The `poloniex.Poloniex(timeout=1)` attribute/arg adjusts the number of seconds to wait for a response from poloniex, else `requests.exceptions.Timeout` is raised (which will be caught by 'poloniex.retry' and attempt the call again).
- If a `requests` exception is raised (including `Timeout`s), signaling that the api call did not go through, the wrapper will attempt to try the call again. The wait pattern between retrys are as follows (in seconds): (0, 2, 5, 30). Once the retry delay list is exausted and the call still throws an error, the list of captured exceptions is raised.
- A call restrictor (`coach`) is enabled by default, limiting the api wrapper to 6 calls per second. If you wish, you can deactivate the coach using `Poloniex(coach=False)` or use an 'external' coach.
- By default, json floats are parsed as strings (ints are ints), you can define `Poloniex(jsonNums=float)` to have _all numbers_ (floats _and_ ints) parsed as floats (or import and use `decimal.Decimal`).
- `poloniex.coach`, `poloniex.retry`, and `poloniex` have self named loggers.

## Usage:
### Basic Public Setup (no api Key/Secret):
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
polo.key = 'your-Api-Key-Here-xxxx'
polo.secret = 'yourSecretKeyHere123456789'
```
Get all your balances
```python
balance = polo.returnBalances()
print("I have %s ETH!" % balance['ETH'])
# or
balance = polo('returnBalances')
print("I have %s BTC!" % balance['BTC'])
```
### Custom/external coach example:
```python
from poloniex import Poloniex, Coach
myCoach = Coach()

public = Poloniex(coach=myCoach)
private = Poloniex(key, secret, coach=myCoach)
# now make calls using both 'private' and 'public' and myCoach will handle both
```

**Examples of WAMP applications using the websocket push API can be found [here](https://github.com/s4w3d0ff/python-poloniex/tree/master/examples).**
