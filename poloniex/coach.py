#    coach.py
#    Copyright (C) 2016  https://github.com/s4w3d0ff
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import logging
from time import sleep, time, gmtime, strftime, strptime, localtime, mktime
from calendar import timegm

# Convertions
def epoch2UTCstr(timestamp=time(), fmat="%Y-%m-%d %H:%M:%S"):
    """
    - takes epoch timestamp
    - returns UTC formated string
    """
    return strftime(fmat, gmtime(timestamp))

def UTCstr2epoch(datestr=epoch2UTCstr(), fmat="%Y-%m-%d %H:%M:%S"):
    """
    - takes UTC date string
    - returns epoch
    """
    return timegm(strptime(datestr, fmat))

def epoch2localstr(timestamp=time(), fmat="%Y-%m-%d %H:%M:%S"):
    """
    - takes epoch timestamp
    - returns localtimezone formated string
    """
    return strftime(fmat, localtime(timestamp))

def localstr2epoch(datestr=epoch2UTCstr(), fmat="%Y-%m-%d %H:%M:%S"):
    """
    - takes localtimezone date string,
    - returns epoch
    """
    return mktime(strptime(datestr, fmat))

def float2roundPercent(floatN, decimalP=2):
    """
    - takes float
    - returns percent(*100) rounded to the Nth decimal place as a string
    """
    return str(round(float(floatN)*100, decimalP))+"%"

# Coach
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
        self._timeFrame, self._callLimit = timeFrame, callLimit
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
