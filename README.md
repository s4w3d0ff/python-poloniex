[![python](https://img.shields.io/badge/python-2.7%20%26%203-blue.svg)![licence](https://img.shields.io/badge/licence-GPL%20v2-blue.svg)](https://github.com/s4w3d0ff/python-poloniex/blob/master/LICENSE) [![release](https://img.shields.io/github/release/s4w3d0ff/python-poloniex.svg)![release build](https://travis-ci.org/s4w3d0ff/python-poloniex.svg?branch=v0.5.7)](https://github.com/s4w3d0ff/python-poloniex/releases)  
[![master](https://img.shields.io/badge/branch-master-blue.svg)![master build](https://api.travis-ci.org/s4w3d0ff/python-poloniex.svg?branch=master)](https://github.com/s4w3d0ff/python-poloniex/tree/master) [![dev](https://img.shields.io/badge/branch-dev-blue.svg)![dev build](https://api.travis-ci.org/s4w3d0ff/python-poloniex.svg?branch=dev)](https://github.com/s4w3d0ff/python-poloniex/tree/dev)  

Inspired by [this](http://pastebin.com/8fBVpjaj) wrapper written by 'oipminer'  
> I (s4w3d0ff) am not affiliated with, nor paid by [Poloniex](https://poloniex.com). If you wish to contribute to the repository please read [CONTRIBUTING.md](https://github.com/s4w3d0ff/python-poloniex/blob/master/CONTRIBUTING.md). All and any help is appreciated.
#### Features:
- [x] Python 2.7 and 3.5+
- [x] Pypi
- [x] Travis
- [x] Websocket api support
- [x] Minimal amount of dependencies
- [x] Internal checks to reduce external api errors
- [x] Rate limiter to keep from going over call limits
- [x] Retries failed api calls during connection issues

### Install:
```
pip install --upgrade poloniexapi
```

### Usage:
See the [wiki](https://github.com/s4w3d0ff/python-poloniex/wiki) or `help(poloniex)` for more.

All api calls are done through an instance of `poloniex.Poloniex`. You can use the instance as follows:
```python
# import this package
from poloniex import Poloniex

# make an instance of poloniex.Poloniex
polo = Poloniex()

# show the ticker
print(polo('returnTicker'))
```
Using the instances `__call__` method (shown above) you can pass the command string as the first argument to make an api call. The `poloniex.Poloniex` class also has 'helper' methods for each command that will help 'sanitize' the commands arguments. For example, `Poloniex.returnChartData('USDT_BTC', period=777)` will raise `PoloniexError("777 invalid candle period")`.

```python
# using a 'helper' method
print(polo.returnChartData(currencyPair='BTC_LTC', period=900))
# bypassing 'helper'
print(polo(command='returnChartData', args={'currencyPair': 'BTC_LTC',
                                            'period': 900}))
```
Almost every api command can be called this way. This wrapper also checks that the command you pass to the `command` arg is a valid command to send to poloniex, this helps reduce api errors due to typos.

#### Private Commands:
To use the private api commands you first need an api key and secret (supplied by poloniex). When creating the instance of `poloniex.Poloniex` you can pass your api key and secret to the object like so:

```python
import poloniex
polo = poloniex.Poloniex(key='your-Api-Key-Here-xxxx', secret='yourSecretKeyHere123456789')

# or this works
polo.key = 'your-Api-Key-Here-xxxx'
polo.secret = 'yourSecretKeyHere123456789'

# get your balances
balance = polo.returnBalances()
print("I have %s ETH!" % balance['ETH'])

# or use '__call__'
balance = polo('returnBalances')
print("I have %s BTC!" % balance['BTC'])
```
#### Trade History:
Poloniex has two api commands with the same name `returnTradeHistory`. To work around this without splitting up the commands or having to specify 'public' or 'private' we use the helper method `Poloniex.marketTradeHist` for public trade history and `Poloniex.returnTradeHistory` for private trades. If you try to bypass the helper method using `Poloniex.__call__`, it will call the private command.

**Public** trade history:
```python
print(polo.marketTradeHist('BTC_ETH'))
```
**Private** trade history:
```python
print(polo.returnTradeHistory('BTC_ETH'))
```

You can also not use the 'helper' methods at all and use `poloniex.PoloniexBase` which only has `returnMarketHist` and `__call__` to make rest api calls.

#### Websocket Usage:
To connect to the websocket api use the `PoloniexSocketed` class like so:
```python
import poloniex
import logging
from time import sleep

# helps show what is going on
logging.basicConfig()
poloniex.logger.setLevel(logging.DEBUG)

def on_volume(data):
    print(data)
# make instance
sock = poloniex.PoloniexSocketed()
# start the websocket thread and subscribe to '24hvolume' setting the callback to 'on_volume'
sock.startws(subscribe={'24hvolume': on_volume})
# give the socket some time to init
sleep(5)
# use the channel name str or id int to subscribe/unsubscribe
sock.subscribe(chan='ticker', callback=print)
sleep(1)
# unsub from ticker using id (str name can be use as well)
sock.unsubscribe(1002)
sleep(4)
# stop websocket
sock.stopws()

```

```
INFO:poloniex:Websocket thread started
DEBUG:poloniex:Subscribed to 24hvolume
[1010]
DEBUG:poloniex:Subscribed to ticker
[241, '86.59997298', '86.68262835', '85.69590501', '0.01882321', '22205.56419338', '258.30264061', 0, '87.31843098', '82.81638725']
...
...
[254, '5.89427014', '6.14542299', '5.92000026', '-0.03420118', '9978.11197201', '1649.83975863', 0, '6.19642428', '5.74631502']
DEBUG:poloniex:Unsubscribed to ticker
[1010]
[1010]
[1010]
['2019-06-07 04:16', 2331, {'BTC': '2182.115', 'ETH': '490.635', 'XMR': '368.983', 'USDT': '7751402.061', 'USDC': '5273463.730'}]
DEBUG:poloniex:Websocket Closed
INFO:poloniex:Websocket thread stopped/joined
```
You can also subscribe and start the websocket thread when creating an instance of `PoloniexSocketed` by using the `subscribe` and `start` args:
```python

sock = poloniex.PoloniexSocketed(subscribe={'24hvolume': print}, start=True)

```


**More examples of how to use websocket push API can be found [here](https://github.com/s4w3d0ff/python-poloniex/tree/master/examples).**
