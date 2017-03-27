#    coach.py
#    Copyright (C) 2016  https://github.com/s4w3d0ff
#    Copyright (C) 2017  https://github.com/metaperl
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
from collections import deque
from time import time, sleep

logger = logging.getLogger(__name__)

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
        self.timeFrame = timeFrame
        self.timeBook = deque(list(), callLimit)

    @property
    def timeOverTimeframe(self):
        elapsed = self.timeBook[-1] - self.timeBook[0]
        logging.debug("Timebook=%s, Elapsed over time frame = %f",
                      self.timeBook, elapsed)
        return elapsed

    def maybeSleep(self):
        if len(self.timeBook) == 1:
            logging.debug("First API call. No need to sleep.")
            return

        requiredElapsed = self.timeOverTimeframe - self.timeFrame
        if requiredElapsed < 0:
            requiredElapsed *= -1
            logging.debug("Need to sleep %f seconds", requiredElapsed)
            sleep(requiredElapsed)

    def wait(self):
        """ Makes sure our api calls don't go past the api call limit """
        self.timeBook.append(time())
        self.maybeSleep()
