# **An API wrapper for Poloniex.com written in Python**
#####poloniex.py - _Tested on Python 2.7.12 & 3.5.2_
Inspired by [this](http://pastebin.com/8fBVpjaj) wrapper written by 'oipminer'

### Features:
- ApiKey and Secret are optional if used for just public commands.
- Api Commands have been 'mapped' into methods within the Poloniex class for your convenience.
- Raises `ValueError` if the command supplied does not exist or if the api keys are not defined
- The `poloniex.Poloniex()` object has an optional 'timeout' attribute/arg that adjusts the number of seconds to wait for a response from polo (default = 3 sec)
- Optional api 'coach' can restrict the amount of calls per sec, keeping your api calls (that aren't threaded) under the limit (6 calls per sec). Activate the coach using `poloniex.Poloniex(coach=True)` when creating the polo object or by defining `polo._coaching = True`.

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
#### **Basic Public Setup (no ApiKey/Secret):**
```python
from poloniex import Poloniex
poloApi = Poloniex()
```
##### Ticker
```python
print(poloApi('returnTicker')['BTC_CGA'])
# or
print(poloApi.returnTicker()['BTC_CGA'])
```
#### Public trade history:
```python
print(poloApi.marketTradeHist('BTC_CGA'))
```

#### **Basic Private Setup (ApiKey/Secret required):**
```python
import poloniex
poloApi = poloniex.Poloniex('your-Api-Key-Here-xxxx','yourSecretKeyHere123456789')
# or
poloApi.APIKey = 'your-Api-Key-Here-xxxx'
poloApi.Secret = 'yourSecretKeyHere123456789'
```
##### Get all your balances
```python
balance = poloApi.returnBalances()
print("I have %s CGA!" % balance['CGA'])
# or
balance = poloApi('returnBalances')
print("I have %s BTC!" % balance['BTC'])
```

#### **Extended Setup:**
```python
from poloniex import Poloniex
poloApi = Poloniex('your-Api-Key-Here-xxxx','yourSecretKeyHere123456789', extend=True)
```
Using `extend=True` will wrap most of the api commands with more 'meaningful' namespaces.
```python
print(poloApi.marketTicker())
print(poloApi.myBalances())
```
See [poloniex/__init__.py#L131](https://github.com/s4w3d0ff/python-poloniex/blob/v0.1.3/poloniex/__init__.py#L131) for more info.

**Examples of WAMP applications using the websocket push API can be found [here](https://github.com/s4w3d0ff/python-poloniex/tree/master/examples).**

You like?!
```
CGA: aZ1yHGx4nA64aWMDNQKXJrojso7gfQ1J5P
BTC: 15D8VaZco22GTLVrFMAehXyif6EGf8GMYV
LTC: LakbntAYrwpVSnLWj1fCLttVzpiDXDa5JV
DOGE: DAQjkQNbhpUoQw7KHAGkDYZ3yySKi751dd
```
