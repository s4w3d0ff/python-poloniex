# Examples
#### _Examples require [this poloniex module](https://github.com/s4w3d0ff/python-poloniex) to be installed._

## Chart:
Saves chart data in a mongodb collection and returns a pandas dataframe with basic indicators.
### Requirements:
pip:
```
pandas
numpy
pymongo
```
Chart examples require [mongod](https://www.mongodb.com/) running locally.

## Loanbot:
Helps your loan offers get filled and keeps them from going 'stale'
### Requirements:
Just [this git repository](https://github.com/s4w3d0ff/python-poloniex).


## Websocket:
Examples of how to use the websocket api to create tickers, stoplimits, etc.
### Requirements:
Just [this git repository](https://github.com/s4w3d0ff/python-poloniex) v0.5+.
`mongoTicker.py` requires pymongo and mongod running.
