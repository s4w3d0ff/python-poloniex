From inside the `examples/loanbot` dir:

```
python loanbot.py 'your-api-key' 'your5uper5ectetH4ash'
```

### What the bot does:
  First the bot turns __off__ auto-renew on all _active_ loan orders.  
  It then loops the following __every 10 min__ until asked to stop:  
    - checks all open loan offers to see if they are 'stale' (older than _30 min_)
    - if an offer is sale, it cancels the offer (making them available in 'lending')
    - the bot then gets current 'lending' account balances
    - checks if the balance of each avail coin is enough to make a decent sized offer
    - finds the current lowest asking rate for each coin we are lending
    - creates a loan offer slightly better then lowest asking rate `6 * loantoshis` `loantoshi = 0.000001`
    - it then prints the current active loans

### Configuring:
  See lines #153-#174
