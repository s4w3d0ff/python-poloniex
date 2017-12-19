# Works on python3 / requires: pandas, numpy, pymongo, bokeh
# BTC: 1A7K4kgXLSSzvDRjvoGwomvhrNU4CKezEp
# LTC: LWShTeRrZpYS4aJhb6JdP3R9tNFMnZiDo2

import logging
from operator import itemgetter
from math import pi
from time import time

from pymongo import MongoClient
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.models import NumeralTickFormatter
from bokeh.models import LinearAxis, Range1d

logger = logging.getLogger(__name__)


def rsi(df, window, targetcol='weightedAverage', colname='rsi'):
    """ Calculates the Relative Strength Index (RSI) from a pandas dataframe
    http://stackoverflow.com/a/32346692/3389859
    """
    series = df[targetcol]
    delta = series.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    # first value is sum of avg gains
    u[u.index[window - 1]] = np.mean(u[:window])
    u = u.drop(u.index[:(window - 1)])
    # first value is sum of avg losses
    d[d.index[window - 1]] = np.mean(d[:window])
    d = d.drop(d.index[:(window - 1)])
    rs = u.ewm(com=window - 1,
               ignore_na=False,
               min_periods=0,
               adjust=False).mean() / d.ewm(com=window - 1,
                                            ignore_na=False,
                                            min_periods=0,
                                            adjust=False).mean()
    df[colname] = 100 - 100 / (1 + rs)
    df[colname].fillna(df[colname].mean(), inplace=True)
    return df


def sma(df, window, targetcol='close', colname='sma'):
    """ Calculates Simple Moving Average on a 'targetcol' in a pandas dataframe
    """
    df[colname] = df[targetcol].rolling(
        min_periods=1, window=window, center=False).mean()
    return df


def ema(df, window, targetcol='close', colname='ema', **kwargs):
    """ Calculates Expodential Moving Average on a 'targetcol' in a pandas
    dataframe """
    df[colname] = df[targetcol].ewm(
        span=window,
        min_periods=kwargs.get('min_periods', 1),
        adjust=kwargs.get('adjust', True),
        ignore_na=kwargs.get('ignore_na', False)
    ).mean()
    df[colname].fillna(df[colname].mean(), inplace=True)
    return df


def macd(df, fastcol='emafast', slowcol='sma', colname='macd'):
    """ Calculates the differance between 'fastcol' and 'slowcol' in a pandas
    dataframe """
    df[colname] = df[fastcol] - df[slowcol]
    return df


def bbands(df, window, targetcol='close', stddev=2.0):
    """ Calculates Bollinger Bands for 'targetcol' of a pandas dataframe """
    if not 'sma' in df:
        df = sma(df, window, targetcol)
    df['sma'].fillna(df['sma'].mean(), inplace=True)
    df['bbtop'] = df['sma'] + stddev * df[targetcol].rolling(
        min_periods=1,
        window=window,
        center=False).std()
    df['bbtop'].fillna(df['bbtop'].mean(), inplace=True)
    df['bbbottom'] = df['sma'] - stddev * df[targetcol].rolling(
        min_periods=1,
        window=window,
        center=False).std()
    df['bbbottom'].fillna(df['bbbottom'].mean(), inplace=True)
    df['bbrange'] = df['bbtop'] - df['bbbottom']
    df['bbpercent'] = ((df[targetcol] - df['bbbottom']) / df['bbrange']) - 0.5
    return df


def plotRSI(p, df, plotwidth=800, upcolor='green', downcolor='red'):
    # create y axis for rsi
    p.extra_y_ranges = {"rsi": Range1d(start=0, end=100)}
    p.add_layout(LinearAxis(y_range_name="rsi"), 'right')

    # create rsi 'zone' (30-70)
    p.patch(np.append(df['date'].values, df['date'].values[::-1]),
            np.append([30 for i in df['rsi'].values],
                      [70 for i in df['rsi'].values[::-1]]),
            color='olive',
            fill_alpha=0.2,
            legend="rsi",
            y_range_name="rsi")

    candleWidth = (df.iloc[2]['date'].timestamp() -
                   df.iloc[1]['date'].timestamp()) * plotwidth
    # plot green bars
    inc = df.rsi >= 50
    p.vbar(x=df.date[inc],
           width=candleWidth,
           top=df.rsi[inc],
           bottom=50,
           fill_color=upcolor,
           line_color=upcolor,
           alpha=0.5,
           y_range_name="rsi")
    # Plot red bars
    dec = df.rsi <= 50
    p.vbar(x=df.date[dec],
           width=candleWidth,
           top=50,
           bottom=df.rsi[dec],
           fill_color=downcolor,
           line_color=downcolor,
           alpha=0.5,
           y_range_name="rsi")


def plotMACD(p, df, color='blue'):
    # plot macd
    p.line(df['date'], df['macd'], line_width=4,
           color=color, alpha=0.8, legend="macd")
    p.yaxis[0].formatter = NumeralTickFormatter(format='0.00000000')


def plotCandlesticks(p, df, plotwidth=750, upcolor='green', downcolor='red'):
    candleWidth = (df.iloc[2]['date'].timestamp() -
                   df.iloc[1]['date'].timestamp()) * plotwidth
    # Plot candle 'shadows'/wicks
    p.segment(x0=df.date,
              y0=df.high,
              x1=df.date,
              y1=df.low,
              color="black",
              line_width=2)
    # Plot green candles
    inc = df.close > df.open
    p.vbar(x=df.date[inc],
           width=candleWidth,
           top=df.open[inc],
           bottom=df.close[inc],
           fill_color=upcolor,
           line_width=0.5,
           line_color='black')
    # Plot red candles
    dec = df.open > df.close
    p.vbar(x=df.date[dec],
           width=candleWidth,
           top=df.open[dec],
           bottom=df.close[dec],
           fill_color=downcolor,
           line_width=0.5,
           line_color='black')
    # format price labels
    p.yaxis[0].formatter = NumeralTickFormatter(format='0.00000000')


def plotVolume(p, df, plotwidth=800, upcolor='green', downcolor='red'):
    candleWidth = (df.iloc[2]['date'].timestamp() -
                   df.iloc[1]['date'].timestamp()) * plotwidth
    # create new y axis for volume
    p.extra_y_ranges = {"volume": Range1d(start=min(df['volume'].values),
                                          end=max(df['volume'].values))}
    p.add_layout(LinearAxis(y_range_name="volume"), 'right')
    # Plot green candles
    inc = df.close > df.open
    p.vbar(x=df.date[inc],
           width=candleWidth,
           top=df.volume[inc],
           bottom=0,
           alpha=0.1,
           fill_color=upcolor,
           line_color=upcolor,
           y_range_name="volume")

    # Plot red candles
    dec = df.open > df.close
    p.vbar(x=df.date[dec],
           width=candleWidth,
           top=df.volume[dec],
           bottom=0,
           alpha=0.1,
           fill_color=downcolor,
           line_color=downcolor,
           y_range_name="volume")


def plotBBands(p, df, color='navy'):
    # Plot bbands
    p.patch(np.append(df['date'].values, df['date'].values[::-1]),
            np.append(df['bbbottom'].values, df['bbtop'].values[::-1]),
            color=color,
            fill_alpha=0.1,
            legend="bband")
    # plot sma
    p.line(df['date'], df['sma'], color=color, alpha=0.9, legend="sma")


def plotMovingAverages(p, df):
    # Plot moving averages
    p.line(df['date'], df['emaslow'],
           color='orange', alpha=0.9, legend="emaslow")
    p.line(df['date'], df['emafast'],
           color='red', alpha=0.9, legend="emafast")


class Charter(object):
    """ Retrieves 5min candlestick data for a market and saves it in a mongo
    db collection. Can display data in a dataframe or bokeh plot."""

    def __init__(self, api):
        """
        api = poloniex api object
        """
        self.api = api

    def __call__(self, pair, frame=False):
        """ returns raw chart data from the mongo database, updates/fills the
        data if needed, the date column is the '_id' of each candle entry, and
        the date column has been removed. Use 'frame' to restrict the amount
        of data returned.
        Example: 'frame=api.YEAR' will return last years data
        """
        # use last pair and period if not specified
        if not frame:
            frame = self.api.YEAR * 10
        dbcolName = pair + 'chart'
        # get db connection
        db = MongoClient()['poloniex'][dbcolName]
        # get last candle
        try:
            last = sorted(
                list(db.find({"_id": {"$gt": time() - 60 * 20}})),
                key=itemgetter('_id'))[-1]
        except:
            last = False
        # no entrys found, get all 5min data from poloniex
        if not last:
            logger.warning('%s collection is empty!', dbcolName)
            new = self.api.returnChartData(pair,
                                           period=60 * 5,
                                           start=time() - self.api.YEAR * 13)
        else:
            new = self.api.returnChartData(pair,
                                           period=60 * 5,
                                           start=int(last['_id']))
        # add new candles
        updateSize = len(new)
        logger.info('Updating %s with %s new entrys!',
                    dbcolName, str(updateSize))

        # show the progess
        for i in range(updateSize):
            print("\r%s/%s" % (str(i + 1), str(updateSize)), end=" complete ")
            date = new[i]['date']
            del new[i]['date']
            db.update_one({'_id': date}, {"$set": new[i]}, upsert=True)
        print('')

        logger.debug('Getting chart data from db')
        # return data from db (sorted just in case...)
        return sorted(
            list(db.find({"_id": {"$gt": time() - frame}})),
            key=itemgetter('_id'))

    def dataFrame(self, pair, frame=False, zoom=False, window=120):
        """ returns pandas DataFrame from raw db data with indicators.
        zoom = passed as the resample(rule) argument to 'merge' candles into a
            different timeframe
        window = number of candles to use when calculating indicators
        """
        data = self.__call__(pair, frame)
        # make dataframe
        df = pd.DataFrame(data)
        # set date column
        df['date'] = pd.to_datetime(df["_id"], unit='s')
        if zoom:
            df.set_index('date', inplace=True)
            df = df.resample(rule=zoom,
                             closed='left',
                             label='left').apply({'open': 'first',
                                                  'high': 'max',
                                                  'low': 'min',
                                                  'close': 'last',
                                                  'quoteVolume': 'sum',
                                                  'volume': 'sum',
                                                  'weightedAverage': 'mean'})
            df.reset_index(inplace=True)

        # calculate/add sma and bbands
        df = bbands(df, window)
        # add slow ema
        df = ema(df, window, colname='emaslow')
        # add fast ema
        df = ema(df, int(window // 3.5), colname='emafast')
        # add macd
        df = macd(df)
        # add rsi
        df = rsi(df, window // 5)
        # add candle body and shadow size
        df['bodysize'] = df['close'] - df['open']
        df['shadowsize'] = df['high'] - df['low']
        df['percentChange'] = df['close'].pct_change()
        df.dropna(inplace=True)
        return df

    def graph(self, pair, frame=False, zoom=False,
              window=120, plot_width=1000, min_y_border=40,
              border_color="whitesmoke", background_color="white",
              background_alpha=0.4, legend_location="top_left",
              tools="pan,wheel_zoom,reset"):
        """
        Plots market data using bokeh and returns a 2D array for gridplot
        """
        df = self.dataFrame(pair, frame, zoom, window)
        #
        # Start Candlestick Plot -------------------------------------------
        # create figure
        candlePlot = figure(
            x_axis_type=None,
            y_range=(min(df['low'].values) - (min(df['low'].values) * 0.2),
                     max(df['high'].values) * 1.2),
            x_range=(df.tail(int(len(df) // 10)).date.min().timestamp() * 1000,
                     df.date.max().timestamp() * 1000),
            tools=tools,
            title=pair,
            plot_width=plot_width,
            plot_height=int(plot_width // 2.7),
            toolbar_location="above")
        # add plots
        # plot volume
        plotVolume(candlePlot, df)
        # plot candlesticks
        plotCandlesticks(candlePlot, df)
        # plot bbands
        plotBBands(candlePlot, df)
        # plot moving aves
        plotMovingAverages(candlePlot, df)
        # set legend location
        candlePlot.legend.location = legend_location
        # set background color
        candlePlot.background_fill_color = background_color
        candlePlot.background_fill_alpha = background_alpha
        # set border color and size
        candlePlot.border_fill_color = border_color
        candlePlot.min_border_left = min_y_border
        candlePlot.min_border_right = candlePlot.min_border_left
        #
        # Start RSI/MACD Plot -------------------------------------------
        # create a new plot and share x range with candlestick plot
        rsiPlot = figure(plot_height=int(candlePlot.plot_height // 2.5),
                         x_axis_type="datetime",
                         y_range=(-(max(df['macd'].values) * 2),
                                  max(df['macd'].values) * 2),
                         x_range=candlePlot.x_range,
                         plot_width=candlePlot.plot_width,
                         title=None,
                         toolbar_location=None)
        # plot macd
        plotMACD(rsiPlot, df)
        # plot rsi
        plotRSI(rsiPlot, df)
        # set background color
        rsiPlot.background_fill_color = candlePlot.background_fill_color
        rsiPlot.background_fill_alpha = candlePlot.background_fill_alpha
        # set border color and size
        rsiPlot.border_fill_color = candlePlot.border_fill_color
        rsiPlot.min_border_left = candlePlot.min_border_left
        rsiPlot.min_border_right = candlePlot.min_border_right
        rsiPlot.min_border_bottom = 20
        # orient x labels
        rsiPlot.xaxis.major_label_orientation = pi / 4
        # set legend
        rsiPlot.legend.location = legend_location
        # set dataframe 'date' as index
        df.set_index('date', inplace=True)
        # return layout and df
        return [[candlePlot], [rsiPlot]], df


if __name__ == '__main__':
    from poloniex import Poloniex
    from bokeh.layouts import gridplot

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("poloniex").setLevel(logging.INFO)
    logging.getLogger('requests').setLevel(logging.ERROR)

    api = Poloniex(jsonNums=float)

    layout, df = Charter(api).graph('USDT_BTC', window=90,
                                    frame=api.YEAR * 12, zoom='1W')
    print(df.tail())
    p = gridplot(layout)
    show(p)
