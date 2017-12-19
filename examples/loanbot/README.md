```
# install wrapper
pip install git+https://github.com/s4w3d0ff/python-poloniex.git

# clone repo
git clone https://github.com/s4w3d0ff/python-poloniex.git

# enter loanbot dir
cd python-poloniex/examples/loanbot

# run bot
python loanbot.py 'your-api-key' 'your5uper5ectetH4ash'
```

### What the bot does:  
* First the bot turns __off__ auto-renew on all _active_ loan orders.  
* It then loops the following __every 5 min__ until asked to stop:  
  - checks all open loan offers to see if they are 'stale' (older than _10 min_)
  - if an offer is stale, it cancels the offer (making them available in 'lending')
  - the bot then gets current 'lending' account balances
  - checks if the balance of each avail coin is enough to make a decent sized offer
  - creates a loan offer whos rate is the average of all open offer rates
  - it then prints the current active loans

### Configuring:
  See lines [#157-#175](https://github.com/s4w3d0ff/python-poloniex/blob/master/examples/loanbot/loanbot.py#L157-#L175)
