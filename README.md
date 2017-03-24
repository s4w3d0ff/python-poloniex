# An API wrapper for Poloniex.com written in Python
Tested on Python 2.7.12 & 3.5.2

Inspired by [this](http://pastebin.com/8fBVpjaj) wrapper written by 'oipminer'
Extended from [s4w3d0ff](https://github.com/s4w3d0ff/python-poloniex/)'s
version

## Extensions from s4w3d0ff

### Unique nonce generation

Instead of setting the nonce, it is dynamically provided on each access.
This eliminates the "stale nonce" errors I was occasionally getting.

### Automatic Retry of HTTP timeouts

If you use this API with any frequency or volume, you will eventually encounter
[HTTPRequest timeout errors from the Requests module](http://docs.python-requests.org/en/master/_modules/requests/exceptions/?highlight=timeout%20exception)

Initially, I was handling this is my own code, but because I was making multiple
calls to the API in different places, it made more sense that [the API itself
would handle this](https://github.com/metaperl/python-poloniex/commit/107667805a900d4acfe731ce1e444dd1157db985).

### API Coach enabled by default

I encountered this error when using python-poloniex:
    {"error":"Please do not make more than 6 API calls per second."}

I noticed that the coach was not enabled by default. So I enabled it.


### constructor option for debugging/logging


### wrapping of return results
Results from API are by default wrapped in a [DotMap](https://pypi.python.org/pypi/dotmap)

You can supply a constructor with a user-supplied class if you want even
further customization of return results.

For instance, I typically wrap Polo with a subclass of DotMap where I
override certain properties and add addtional properties.


## Features:
- Key and Secret are optional if used for just public commands.
- Api Commands have been 'mapped' into methods within the Poloniex class for your convenience.
- Raises `ValueError` if the command supplied does not exist or if the api keys are not defined
- The `poloniex.Poloniex()` object has an optional 'timeout' attribute/arg that adjusts the number of seconds to wait for a response from polo (default = 3 sec)
- Optional api 'coach' can restrict the amount of calls per sec, keeping your api calls (that aren't threaded) under the limit (6 calls per sec). Activate the coach using `poloniex.Poloniex(coach=True)` when creating the polo object or by defining `polo._coaching = True`.

## Install:
Python 2:
```
pip install git+https://github.com/metaperl/python-poloniex.git
```

Python 3:
```
pip3 install git+https://github.com/metaperl/python-poloniex.git
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
