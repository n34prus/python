# -*- coding: cp1251 -*-
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os

# ����������� �������� ����� � ������� ����� ������� ������
# cmd = 'mode 250,70'
# os.system(cmd)
pd.set_option("display.max_columns", None)
pd.set_option('display.width', 2000)

# ��������� ��������� �� �����������:
# marking - �������� ��������� ����� ����� � ������ � ������ �� ��������� ������������ ������, ����� ����� ��� �������� ��������
# macd - �������� ����� �����/������ �� MACD
# macdex - �������� ����� �����/������ �� ��������� ����������� ���������� MACD
# trend - �������� �� ��������� ������� ���������� (��������� ������)
def apply_indicator(_df, _method='marking', _interpolate=0):
    # ������ ������ � ����������
    _df.columns = [x.lower() for x in _df.columns]
    if _interpolate:
        # ������� ������������� �������� � �� ������ ���� ��� ������ ������
        # �� �������� ������������ ������ ����� ����������
        _deltaT = _df.shift(1).first_valid_index() - _df.first_valid_index()  # ����������� ���������
        date_index = pd.date_range(start='11/30/2021 20:00', periods=48, freq='H', tz=0)
        # print("\nold indexes: ", _df.index)
        # print("\nnew indexes: ", date_index)
        _df = _df.reindex(date_index)
        _df = _df.interpolate()
    if _method == 'marking':
        # ���� ���� �������
        _df['dif'] = _df['close'].diff()
        # ���� ���� �������
        _df['signdif'] = _df['dif'] >= 0
        # �������� ��������� ����������
        _df['extremum'] = _df['signdif'].diff()
        # print(df3)
        # ������� � ������ ����������� �����
        _df['buy'] = (_df['extremum'] == True) & (_df['signdif'] == True)
        # ������� � ������ ����������� ������
        _df['sold'] = (_df['extremum'] == True) & (_df['signdif'] == False)
        # �������� �� �� ��� �����. ���� ��� �������� ����� � ��� ����� ��������� �� ���� ������ ������ :)
        _df['buy'] = _df['buy'].shift(-1)
        _df['sold'] = _df['sold'].shift(-1)
        return _df
    elif _method == 'macd':
        # ��������� MACD: macdh ��� �����������, macds ��� ��������� ���������� �������, macd ��� macd :)
        _df.ta.macd(close='close', fast=12, slow=26, append=True)
        _df.columns = [x.lower() for x in _df.columns]
        # ��������� ������� ������� slow � macd
        _df['sign'] = _df['macds_12_26_9'] < _df['macd_12_26_9']
        # ��������� ����� ����� (������ ����������� ��������)
        _df['cross'] = _df['sign'].diff()
        # ������� � ������ ����������� �����
        _df['buy'] = (_df['cross'] == True) & (_df['sign'] == True)
        # ������� � ������ ����������� ������
        _df['sold'] = (_df['cross'] == True) & (_df['sign'] == False)
        return _df
    elif _method == 'macdex':
        _df.ta.macd(close='close', fast=12, slow=26, append=True)
        _df.columns = [x.lower() for x in _df.columns]
        # ��������������
        _df['dif'] = _df['macd_12_26_9'].diff()
        # ���� ���� �������
        _df['signdif'] = _df['dif'] >= 0
        # �������� ��������� ����������
        _df['extremum'] = _df['signdif'].diff()
        # ������� � ������ ����������� �����
        _df['buy'] = (_df['extremum'] == True) & (_df['signdif'] == True) & (np.isnan(_df['macds_12_26_9']) == False)
        # ������� � ������ ����������� ������
        _df['sold'] = (_df['extremum'] == True) & (_df['signdif'] == False) & (np.isnan(_df['macds_12_26_9']) == False)
        return _df
    # ���� ������� ����������. ������� ��������� ������ ������� n*n ��������� ���� �������.
    # �� ����� N ������������ ������. ��� ������ �� 0 �� N/2 ������ ���������: �������� �� ���� �������� ������ ����� �������� �������� ����� 0.
    # ������������ ���������� ����� � ���� ������� f(t) ��� f - ���������� �� ���������� ���� ��������� ��� ������ ������.
    # ��� ������ �� N/2+1 �� N ������ ���������: �������� �� ���� �������� �������� �������� ����� N/2+1
    # ���������� ��������������� ������ �������� ������� g(t). ������� ��������, ��� t ������ ���������� � ��������� 0..N/2, � �� N/2+1..N
    #
    # ��. ������� ���. ����� N ������, �� ���� �������� �������� ���� �������� ������ �����, �������� ����� �������� - ������������� ������������ ������ �����
    # ���� �������� ����� ����� ���������� � ������� ����� ����� ���������. ���������� �� �� ������, ���������� ����� � ��� ���� ����� �������� �� ���� �����!
    # �������� ��������������� ��������, ��� ��� ����� � ��������� �� -1 �� 1 � � ���� ����� ��������
    # ������ ������� N*2 ��� ������ ������� - ��������������� ���� ��������, � ������ - ����
    # ������ ���������� �� ����� �������. ������ ������� ����� �������, � ������ - �������� ��������� � ������
    # ���� 1 - � ��� ����, ���� -1 - � ��� ������ �����, ���� 0 - �� � ������� ������
    # �������� �� -1 ��������: -1 ����, 0 �����, 1 �����.
    # ���������� 1 ��������: 0 ����, 0.5 �����, 1 �����.
    # �������� �� ���� ���������������� �������� ��������� ������, �������� ������� ����� ��������� �� -1 (����� ����) �� 1 (����� �����), 0 - ������������
    # ���������� ����� �������, �� �������� ����
    elif _method == 'trend':
        #_df = _df.astype(object)
        #_df['new'] = _df.apply(lambda r: list(r), axis=1)#.apply(np.array)
        _df['doparr'] = _df.apply(lambda x: list([]), axis=1)
        for i in range(3):
            _df['dop' + str(i + 1)] = _df.shift(i + 1)['open']
            _df['dcl' + str(i + 1)] = _df.shift(i + 1)['close']
            _df['dmx' + str(i + 1)] = _df.shift(i + 1)['high']
            _df['dmn' + str(i + 1)] = _df.shift(i + 1)['low']
            #_df['doparr'] = _df.apply(lambda x: list([x['dop' + str(i + 1)]]), axis=1)
            _df['doparr'] = _df.apply(lambda x: x['doparr'] + [x['dop' + str(i + 1)]], axis=1)

        #works! _df['wat'] = _df.apply(lambda x: list([x['dop1'], x['dcl1']]), axis=1)
        #_df['difo'] =
        #_df['difc']
        #_df['difmax']
        #_df['difmin']
        #_df['']
        print(_df)

        _df['buy'] = False
        _df['sold'] = False
        return _df
    return _df


def normalise(_df):  # �������� ������ � ������� ��� ��������� � ��������� ���
    # ��������� ������� ���������� NaN ����� ������ ��� ����������
    _df.loc[_df['buy'] == False, 'buy'] = np.nan
    _df.loc[_df['sold'] == False, 'sold'] = np.nan

    # ���������� ��� ��������� ����������, False ���� ������� � True ���� �������.
    # _df.loc[(_df['sold'] == True) & np.isnull(_df['macds_12_26_9']), 'sold'] = False
    # _df.loc[(_df['sold'] == True) & (_df['macds_12_26_9'].isnull()), 'sold'] = False
    # ��������� ������� ���������� ���� �������� ����������
    # _df.loc[_df['buy'] == True, 'lasttrans'] = True
    # _df.loc[_df['sold'] == True, 'lasttrans'] = False
    # _df.loc[(_df['lasttrans'] != True) & (_df['lasttrans'] != False), 'lasttrans'] = _df['lasttrans'].shift(1)
    # _df.loc[(_df['lasttrans'] != True) & (_df['lasttrans'] != False), 'lasttrans'] = _df['lasttrans'].shift(1)
    # �� ���� ������ ������� ���� �� ������� �� ������� ������� � ������������ ������� ����� �� ��������� ���������� ���� ����� ������ ���������
    # _df.loc[(_df['lasttrans'] == _df['buy']) | (_df['lasttrans'] == _df['sold']), 'lasttrans'] = _df['lasttrans'].shift(1)
    # �� �������� ��� ��� ��� ����� �� ���� � ������� �� ���������. �����. ����� ��������� ��� � ���� ������.
    return _df


def calculate_transaction(_df):  # ������� ������ (expense) � ������ (income) �� ����� ����������
    # ���, ��� ��������� �����, ������� �������� ��� ���:
    # ��������� ������ ������ ������� � �������
    fsi = _df[_df.sold == True].first_valid_index()
    fbi = _df[_df.buy == True].first_valid_index()
    # print ('first valid index is ', a)
    # ���� ������� ���� ������ �������, �� �� ���������� ����������
    # (��� � ������� sold, �� ��� ����� �.�. ������� �� ����� �������������� �� �������, � � ���� � ������)
    # if fsi < fbi:
    #    _df.loc[_df.index == fsi, 'sold'] = np.nan
    # � ������ � ����! �� ������� sold � ��������� ������ �� ��������� ��� ���������� � ������� :
    _df.loc[_df['sold'] == True, 'income'] = _df['close']
    _df.loc[_df['buy'] == True, 'expense'] = _df['close']
    try:
        if fsi < fbi:
            _df.loc[_df.index == fsi, 'income'] = np.nan
        # ������ �� ��������� ��������� ������� ���� �� ��� �� ���� �������, ����� ����� ������ ��������� �������:
        # ���� ������� ��������� ������� � �������
        lsi = _df.iloc[::-1][_df.sold == True].first_valid_index()
        lbi = _df.iloc[::-1][_df.buy == True].first_valid_index()
        # ��������� ��������� ������� �� �������� �������
        if lsi < lbi:
            _df.loc[_df.index == lbi, 'expense'] = np.nan
    except Exception:
        print('cant calculate transaction')
    return _df


def show_indicator_plot(_df):  # ������ ��������
    # Construct a 2 x 1 Plotly figure
    fig = make_subplots(rows=2, cols=1)
    # price Line
    fig.append_trace(
        go.Scatter(
            x=_df.index,
            y=_df['open'],
            line=dict(color='#555555', width=1),
            name='open',
            legendgroup='1',
        ), row=1, col=1
    )
    # Candlestick chart for pricing
    fig.append_trace(
        go.Candlestick(
            x=_df.index,
            open=_df['open'],
            high=_df['high'],
            low=_df['low'],
            close=_df['close'],
            increasing_line_color='#ff9922',
            decreasing_line_color='#7777AA',
            showlegend=False
        ), row=1, col=1
    )
    # Fast Signal (%k)
    fig.append_trace(
        go.Scatter(
            x=_df.index,
            y=_df['macd_12_26_9'],
            line=dict(color='#ff9922', width=2),
            name='macd',
            legendgroup='2',
        ), row=2, col=1
    )
    # Slow signal (%d)
    fig.append_trace(
        go.Scatter(
            x=_df.index,
            y=_df['macds_12_26_9'],
            line=dict(color='#7777AA', width=2),
            legendgroup='2',
            name='signal'
        ), row=2, col=1
    )

    # Buy signal
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['close'] * _df['buy'],
            marker=dict(color='#77FF77', size=8, line=dict(color='black', width=1)),
            legendgroup='2',
            name='buy'
        ), row=1, col=1
    )
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['macd_12_26_9'] * _df['buy'],
            marker=dict(color='#77FF77', size=8, line=dict(color='black', width=1)),
            showlegend=False,
            legendgroup='2',
            name='buy'
        ), row=2, col=1
    )

    # Sold signal
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['close'] * _df['sold'],
            marker=dict(color='#FF0000', size=8, line=dict(color='black', width=1)),
            legendgroup='2',
            name='sold'
        ), row=1, col=1
    )
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['macd_12_26_9'] * _df['sold'],
            marker=dict(color='#FF0000', size=8, line=dict(color='black', width=1)),
            showlegend=False,
            legendgroup='2',
            name='sold'
        ), row=2, col=1
    )

    # Colorize the histogram values
    colors = np.where(_df['macdh_12_26_9'] < 0, '#7777AA', '#ff9922')
    # Plot the histogram
    fig.append_trace(
        go.Bar(
            x=_df.index,
            y=_df['macdh_12_26_9'],
            name='histogram',
            marker_color=colors,
        ), row=2, col=1
    )
    # Make it pretty
    layout = go.Layout(
        plot_bgcolor='#efefef',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    # Update options and show plot
    fig.update_layout(layout)
    fig.show()


def show_basic_plot(_df):  # ������ ��������
    # Construct a 2 x 1 Plotly figure
    fig = make_subplots(rows=1, cols=1)
    # price Line
    fig.append_trace(
        go.Scatter(
            x=_df.index,
            y=_df['open'],
            line=dict(color='#555555', width=1),
            name='open',
            legendgroup='1',
        ), row=1, col=1
    )
    # Candlestick chart for pricing
    fig.append_trace(
        go.Candlestick(
            x=_df.index,
            open=_df['open'],
            high=_df['high'],
            low=_df['low'],
            close=_df['close'],
            increasing_line_color='#ff9922',
            decreasing_line_color='#7777AA',
            showlegend=False
        ), row=1, col=1
    )

    # Buy signal
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['close'] * _df['buy'],
            marker=dict(color='#77FF77', size=8, line=dict(color='black', width=1)),
            legendgroup='2',
            name='buy'
        ), row=1, col=1
    )

    # Sold signal
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['close'] * _df['sold'],
            marker=dict(color='#FF0000', size=8, line=dict(color='black', width=1)),
            legendgroup='2',
            name='sold'
        ), row=1, col=1
    )

    # Make it pretty
    layout = go.Layout(
        plot_bgcolor='#efefef',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    # Update options and show plot
    fig.update_layout(layout)
    fig.show()


def show_plot(_df, _method='marking'):  # ������ ��������
    if _method == 'marking':
        fig = make_subplots(rows=1, cols=1)
    else:
        fig = make_subplots(rows=2, cols=1)
    # ������� ������
    fig.append_trace(
        go.Scatter(
            x=_df.index,
            y=_df['open'],
            line=dict(color='#555555', width=1),
            name='open',
            legendgroup='1',
        ), row=1, col=1
    )
    fig.append_trace(
        go.Candlestick(
            x=_df.index,
            open=_df['open'],
            high=_df['high'],
            low=_df['low'],
            close=_df['close'],
            increasing_line_color='#ff9922',
            decreasing_line_color='#7777AA',
            showlegend=False
        ), row=1, col=1
    )
    # Buy
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['close'] * _df['buy'],
            marker=dict(color='#77FF77', size=8, line=dict(color='black', width=1)),
            legendgroup='2',
            name='buy'
        ), row=1, col=1
    )
    # Sold
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['close'] * _df['sold'],
            marker=dict(color='#FF0000', size=8, line=dict(color='black', width=1)),
            legendgroup='2',
            name='sold'
        ), row=1, col=1
    )

    # macd / macdex
    if (_method == 'macd')or(_method == 'macdex'):
        # Fast Signal
        fig.append_trace(
            go.Scatter(
                x=_df.index,
                y=_df['macd_12_26_9'],
                line=dict(color='#ff9922', width=2),
                name='macd',
                legendgroup='2',
            ), row=2, col=1
        )
        # Slow signal
        fig.append_trace(
            go.Scatter(
                x=_df.index,
                y=_df['macds_12_26_9'],
                line=dict(color='#7777AA', width=2),
                legendgroup='2',
                name='signal'
            ), row=2, col=1
        )
        # Buy
        fig.append_trace(
            go.Scatter(
                mode='markers',
                x=_df.index,
                y=_df['macd_12_26_9'] * _df['buy'],
                marker=dict(color='#77FF77', size=8, line=dict(color='black', width=1)),
                showlegend=False,
                legendgroup='2',
                name='buy'
            ), row=2, col=1
        )
        # Sold
        fig.append_trace(
            go.Scatter(
                mode='markers',
                x=_df.index,
                y=_df['macd_12_26_9'] * _df['sold'],
                marker=dict(color='#FF0000', size=8, line=dict(color='black', width=1)),
                showlegend=False,
                legendgroup='2',
                name='sold'
            ), row=2, col=1
        )
        # Colorize the histogram values
        colors = np.where(_df['macdh_12_26_9'] < 0, '#7777AA', '#ff9922')
        # Plot the histogram
        fig.append_trace(
            go.Bar(
                x=_df.index,
                y=_df['macdh_12_26_9'],
                name='histogram',
                marker_color=colors,
            ), row=2, col=1
        )
    # Make it pretty
    layout = go.Layout(
        plot_bgcolor='#efefef',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    # Update options and show plot
    fig.update_layout(layout)
    fig.show()



def calc_profit(_df):  # ������� ������ �� ������� ���������� ����� ���������� ��������, ��������� � ������� ��������
    # ��������� �������
    expense = _df['expense'].sum()
    # ��������� �����
    income = _df['income'].sum()
    # �������
    profit = income - expense
    # ������� � % �� ��������� ������ �������
    try:
        fbi = _df[_df.buy == True].first_valid_index()
        fbv = _df['close'][fbi]
        profitPercent = round(profit / fbv * 100, 2)
    except Exception:
        print('cant calculate profit')
        return
    # ��� ������� ��� ��������� ��������� ��������� � ��������:
    # ��� ���� �� ���� �� �� ������ ���������� ������� � ������ ������� � ������� � ����� ��� ���� ����
    passiveProfit = _df['close'][_df.index[-1]] - _df['close'][_df.index[0]]
    passiveProfitPercent = round(passiveProfit / _df['close'][_df.index[0]] * 100, 2)
    # ������� ��� ������
    print('expense = ', expense)
    print('income = ', income)
    print('first buy =', fbv)
    print('profit = ', profit, ' (', profitPercent, '%)')
    print('passive profit = ', passiveProfit, ' (', passiveProfitPercent, '%)')


def print_df(_df, _feature=np.nan, _condition=True):  # ������� ���� � �������� _condition(_feature)
    # ����� ��� ��������
    if _feature == np.nan:
        print(_df)
    else:
        print(_df[_df[_feature] == _condition])

    # ������ ����������� ���������� � macd
    # printDf(df1, 'cross') ������������:
    # print(df1[df1['cross'] == True])


def analyze_df(_df, _method='marking', _interpolate=0):  # ������� �������� ������
    print("\nCalculating.\nMethod:", _method, "\nInterpolation:", _interpolate)
    _df = apply_indicator(_df, _method, _interpolate)
    _df = normalise(_df)
    _df = calculate_transaction(_df)
    calc_profit(_df)
    show_plot(_df, _method)


########################### MAIN CODE ##############################

### ��� �������� ������ ��� ������� (���������� � Yahoo Finance)                                                                                    ###
# ����� ���� �� ��������� ��� �� ������� �������
df = yf.Ticker('FB').history(period='1y')[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# ����
# df = yf.Ticker('ETH-BTC').history(start="2021-10-20", end="2021-11-19", interval="15m")[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# ���� ������� � ���� �� ��������� ��� �� ������� �������
# df = yf.Ticker('EURUSD=X').history(start="2015-02-01", end="2020-01-01", interval="1d")[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# ���� ����� �� ��������� ��� �� ������� �������
# df = yf.Ticker('BTC-USD').history(period='1y')[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# ���� ����� �� ��������� ��� ������ �� ������� �������
# df = yf.Ticker('BTC-USD').history(start="2021-11-01", end="2021-12-11", interval="1h")[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
analyze_df(df, 'macd')

# printDf(df3, 'extremum')
# print(df3.head(50))
# print(df3.tail(50))
