# Examples

#### _Examples require the poloniex module and/or autobahn installed._

##Push Api Setup 
See http://autobahn.ws/python/installation.html for more details on other systems.
### From fresh Ubuntu install (14.04, 16.04):
#####Python 2.7
```
sudo apt-get install build-essential libssl-dev python-pip python-dev libffi-dev git
sudo bash -c 'apt-get update && apt-get upgrade'
pip install service_identity
pip install autobahn[twisted]
```
#####Python 3
```
sudo apt-get install build-essential libssl-dev python3-pip python3-dev libffi-dev git
sudo bash -c 'apt-get update && apt-get upgrade'
pip3 install service_identity
pip3 install autobahn[twisted]
```
```
git clone https://github.com/s4w3d0ff/python-poloniex.git && cd python-poloniex/examples
python polocalbox.py
# or
python3 polocalbox.py
```
>NOTE: There is also another wonderful api wrapper that wraps the WAMP polo api using asyncio:

>[https://github.com/absortium/poloniex-api](https://github.com/absortium/poloniex-api)
