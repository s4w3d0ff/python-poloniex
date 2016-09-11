from time import sleep, time

class Coach(object):
    """
    Coaches the api wrapper, makes sure it doesn't get all hyped up on Mt.Dew
    Poloniex default call limit is 6 calls per 1 sec.
    """
    def __init__(self, timeFrame=1.0, callLimit=6):
        """
        timeFrame = float time in secs [default = 1.0]
        callLimit = int max amount of calls per 'timeFrame' [default = 6]
        """
        self._timeFrame, self._callLimit = [timeFrame, callLimit]
        self._timeBook = []

    def wait(self):
        """ Makes sure our api calls don't go past the api call limit """
        # what time is it?
        now = time()
        # if it's our turn
        if len(self._timeBook) is 0 or \
                (now - self._timeBook[-1]) >= self._timeFrame:
            # add 'now' to the front of 'timeBook', pushing other times back
            self._timeBook.insert(0, now)
            logging.info(
                "Now: %d  Oldest Call: %d  Diff: %f sec" %
                (now, self._timeBook[-1], now - self._timeBook[-1])
                )
            # 'timeBook' list is longer than 'callLimit'?
            if len(self._timeBook) > self._callLimit:
                # remove the oldest time
                self._timeBook.pop()
        else:
            logging.info(
                "Now: %d  Oldest Call: %d  Diff: %f sec" %
                (now, self._timeBook[-1], now - self._timeBook[-1])
                )
            logging.info(
                "Waiting %s sec..." %
                str(self._timeFrame-(now - self._timeBook[-1]))
                )
            # wait your turn (maxTime - (now - oldest)) = time left to wait
            sleep(self._timeFrame-(now - self._timeBook[-1]))
            # add 'now' to the front of 'timeBook', pushing other times back
            self._timeBook.insert(0, time())
            # 'timeBook' list is longer than 'callLimit'?
            if len(self._timeBook) > self._callLimit:
                # remove the oldest time
                self._timeBook.pop()
