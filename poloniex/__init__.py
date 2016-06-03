import sys
if sys.version_info[0] == 3: # could be better
	from .poloniex import *
else: # good
	from poloniex import *
