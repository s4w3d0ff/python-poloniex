#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://github.com/s4w3d0ff/python-poloniex
# BTC: 1A7K4kgXLSSzvDRjvoGwomvhrNU4CKezEp
#
#    Copyright (C) 2019  https://github.com/s4w3d0ff
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
import poloniex
import tqdm
import pymongo
import pandas as pd

import logging
from time import time, gmtime, strftime, strptime
from calendar import timegm


DB = pymongo.MongoClient()


def epoch2UTCstr(timestamp=False, fmat="%Y-%m-%d %H:%M:%S"):
    """
    - takes epoch timestamp
    - returns UTC formated string
    """
    if not timestamp:
        timestamp = time()
    return strftime(fmat, gmtime(timestamp))

def UTCstr2epoch(datestr=False, fmat="%Y-%m-%d %H:%M:%S"):
    """
    - takes UTC date string
    - returns epoch
    """
    if not datestr:
        datestr = epoch2UTCstr()
    return timegm(strptime(datestr, fmat))

def zoomOHLC(df, zoom):
    """ Resamples a ohlc df """
    df.reset_index(inplace=True)
    df.set_index('date', inplace=True)
    df = df.resample(rule=zoom,
                     closed='left',
                     label='left').apply({'_id': 'first',
                                          'open': 'first',
                                          'high': 'max',
                                          'low': 'min',
                                          'close': 'last',
                                          'quoteVolume': 'sum',
                                          'volume': 'sum',
                                          'weightedAverage': 'mean'})
    df.reset_index(inplace=True)
    return df.set_index('_id')

def getDatabase(db):
    """ Returns a mongodb database """
    return DB[db]

def getLastEntry(db):
    """ Get the last entry of a collection """
    return db.find_one(sort=[('_id', pymongo.DESCENDING)])

def updateChartData(db, data):
    """ Upserts chart data into db with a tqdm wrapper. """
    for i in tqdm.trange(len(data)):
        db.update_one({'_id': data[i]['date']}, {
                      "$set": data[i]}, upsert=True)

def getChartDataFrame(db, start):
    """
    Gets the last collection entrys starting from 'start' and puts them in a df
    """
    try:
        df = pd.DataFrame(list(db.find({"_id": {"$gt": start}})))
        # set date column to datetime
        df['date'] = pd.to_datetime(df["_id"], unit='s')
        df.set_index('_id', inplace=True)
        return df
    except Exception as e:
        logger.exception(e)
        return False


class CPoloniex(poloniex.Poloniex):
    def __init__(self, *args, **kwargs):
        super(CPoloniex, self).__init__(*args, **kwargs)
        if not 'jsonNums' in kwargs:
            self.jsonNums = float
        self.db = getDatabase('poloniex')

    def chartDataFrame(self, pair, frame=172800, zoom=False):
        """ returns chart data in a dataframe from mongodb, updates/fills the
        data, the date column is the '_id' of each candle entry. Use 'frame' to
        restrict the amount of data returned.
        Example: 'frame=self.YEAR' will return last years data
        """
        dbcolName = pair.upper() + '-chart'

        # get db collection
        db = self.db[dbcolName]

        # get last candle data
        last = getLastEntry(db)

        # no entrys found, get all 5min data from poloniex
        if not last:
            self.logger.warning('%s collection is empty!', dbcolName)
            last = {
                '_id': UTCstr2epoch("2015-01-01", fmat="%Y-%m-%d")
                }

        stop = int(last['_id'])
        start = time()
        end = time()
        flag = True
        while not int(stop) == int(start) and flag:
            # get 3 months of data at a time
            start -= self.MONTH * 3

            # dont go past 'stop'
            if start < stop:
                start = stop

            # get needed data
            self.logger.debug('Getting %s - %s %s candles from Poloniex...',
                              epoch2UTCstr(start), epoch2UTCstr(end), pair)
            new = self.returnChartData(pair,
                                       period=60 * 5,
                                       start=start,
                                       end=end)

            # stop if data has stopped comming in
            if len(new) == 1:
                flag = False

            # add new candles
            self.logger.debug(
                'Updating %s database with %s entrys...', pair, str(len(new))
                )
            updateChartData(db, new)

            # make new end the old start
            end = start

        # make dataframe
        self.logger.debug('Getting %s chart data from db', pair)
        df = getChartDataFrame(db, time() - frame)

        # adjust candle period 'zoom'
        if zoom:
            df = zoomOHLC(df, zoom)

        return df

if __name__ == '__main__':
    logging.basicConfig()
    polo = CPoloniex()
    polo.logger.setLevel(logging.DEBUG)
    print(polo.chartDataFrame(pair='BTC_LTC', frame=polo.WEEK, zoom='3H'))
