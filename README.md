# **An API wrapper for Poloniex.com written in Python**  
![master](https://api.travis-ci.org/s4w3d0ff/python-poloniex.svg?branch=master)  
Inspired by [this](http://pastebin.com/8fBVpjaj) wrapper written by 'oipminer'

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

### Features:
- The first 2 args in the `poloniex.Poloniex` object (`Key` and `Secret`) are _optional_ when used for _public api commands_.
- Api commands have been 'mapped' into methods within the `Poloniex` class for your convenience.
- Raises `poloniex.PoloniexError` if the command supplied does not exist, if the api keys are not defined and attempting to access a private api command, or if Poloniex.com returns an api error.
- The `poloniex.Poloniex(timeout=1)` attribute/arg adjusts the number of seconds to wait for a response from poloniex, else `requests.exceptions.Timeout` is raised (which will be caught by 'poloniex.retry' and attempt the call again).
- If a `requests` exception is raised (including `Timeout`s), signaling that the api call did not go through, the wrapper will attempt to try the call again. The wait pattern between retrys are as follows (in seconds): (0, 2, 5, 30). Once the retry delay list is exausted and the call still throws an error, the list of captured exceptions is raised.
- A call restrictor (`coach`) is enabled by default, limiting the api wrapper to 6 calls per second. If you wish, you can deactivate the coach using `Poloniex(coach=False)` or use an 'external' coach.
- By default, json floats are parsed as strings (ints are ints), you can define `Poloniex(jsonNums=float)` to have _all numbers_ (floats _and_ ints) parsed as floats (or import and use `decimal.Decimal`).
- `poloniex.coach`, `poloniex.retry`, and `poloniex` have self named loggers.

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
### Custom/external coach example:
```python
from poloniex import Poloniex, Coach
myCoach = Coach()

public = Poloniex(coach=myCoach)
private = Poloniex(Key, Secret, coach=myCoach)
# now make calls using both 'private' and 'public' and myCoach will handle both
```

**Examples of WAMP applications using the websocket push API can be found [here](https://github.com/s4w3d0ff/python-poloniex/tree/master/examples).**
