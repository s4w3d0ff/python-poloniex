# Examples

#### _Examples require the poloniex module and/or autobahn installed._

##Push Api Setup (see: http://autobahn.ws/python/installation.html)
### From fresh Ubuntu 14.04 install (Python 2.7):
```bash
sudo apt-get install build-essential libssl-dev python-pip python-dev libffi-dev git
sudo bash -c 'apt-get update && apt-get upgrade'
sudo pip install pyOpenSSL
sudo pip install service_identity
sudo pip install autobahn[twisted]
git clone https://github.com/s4w3d0ff/python-poloniex.git && cd python-poloniex
sudo python setup install
cd examples
python polocalbox.py
python tickercatcher.py
```
