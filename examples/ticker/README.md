## Ticker Examples
Most examples require [mongodb](https://docs.mongodb.com/manual/installation/) and/or this repo installed  

#### dumbTicker.py
Uses the REST api at a set interval to fill ticker data in a local mongodb  
requires: `pandas pymongo`

#### wsMongoTicker.py
Uses the undocumented websocket api to save pushed data in a local mongodb  
requires: `websocket-client pymongo`

#### mongoTicker.py (buggy)
Uses WAMP api to save ticker data in a local mongodb  
requires: `autobahn twisted pymongo`

#### queuedTicker.py (buggy)
Uses WAMP api to save ticker data in memory using a dict  
requires: `autobahn twisted`
