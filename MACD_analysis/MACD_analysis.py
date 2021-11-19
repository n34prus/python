import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os

#����������� �������� ����� � ������� ����� ������� ������
cmd = 'mode 250,70'
os.system(cmd)
pd.set_option("display.max_columns", None)
pd.set_option('display.width', 2000)

### ��� �������� ������ ��� ������� (���������� � Yahoo Finance)                                                                                    ###
#����� ���� �� ��������� ��� �� ������� �������
#df = yf.Ticker('FB').history(period='1y')[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]

#���� ����� �� ��������� ��� �� ������� �������
#df = yf.Ticker('BTC-USD').history(period='1y')[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]

#���� ����� �� ��������� ��� ������ �� ������� �������
df = yf.Ticker('BTC-USD').history(start="2021-10-20", end="2021-11-17", interval="1h")[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]

### ��� �������� ������ ��������������� � �������� ��������                                                                                         ###
# ��������� MACD: macdh ��� �����������, macds ��� ��������� ���������� �������, macd ��� macd :)
df.ta.macd(close='close', fast=12, slow=26, append=True)
# ������ ������ � ����������
df.columns = [x.lower() for x in df.columns]
#��������� ������� ������� slow � macd
df['sign'] = df['macds_12_26_9'] < df['macd_12_26_9']
#��������� ����� ����� (������ ����������� ��������)
df['cross'] = df['sign'].diff()

### ��� �������� MACD ���� df1 (�� ���� ��� �������������� ����� �������� ������� ���� ������ ������ ���������� ����� ������)                       ###
df1 = df.copy(deep = True)
#������� � ������ ����������� �����
df1['buy'] = (df1['cross'] == True) & (df1['sign'] == True)
#������� � ������ ����������� ������
df1['sold'] = (df1['cross'] == True) & (df1['sign'] == False)

### ��� ������������ MACD ���� df2, �������� ����������� ��������� �������� ��� ������ �������� ������������� �� ���� ������                        ###
df2 = df.copy(deep = True)
#����� �������) ������� ����� ��������� ���������� ����� ���������� ���������

### ��� ��������� ����������� MACD ���� df3, �������� �������� �� ����������, ���� ����������� ��������� �� ��������� ������� ����!                 ###
df3 = df.copy(deep = True)
#��������������
df3['dif'] = df3['macd_12_26_9'].diff()
#���� ���� �������
df3['signdif'] = df3['dif'] >= 0
#�������� ��������� ����������
df3['extremum'] = df3['signdif'].diff()
#print(df3)
#������� � ������ ����������� �����
df3['buy'] = (df3['extremum'] == True) & (df3['signdif'] == True) & (np.isnan(df3['macds_12_26_9']) == False)
#������� � ������ ����������� ������
df3['sold'] = (df3['extremum'] == True) & (df3['signdif'] == False) & (np.isnan(df3['macds_12_26_9']) == False)

def normalise(_df):     #�������� ������ � ������� ��� ��������� � ��������� ���
    #��������� ������� ���������� NaN ����� ������ ��� ����������
    _df.loc[_df['buy'] == False, 'buy'] = np.nan
    _df.loc[_df['sold'] == False, 'sold'] = np.nan


    #���������� ��� ��������� ����������, False ���� ������� � True ���� �������. 
    #_df.loc[(_df['sold'] == True) & np.isnull(_df['macds_12_26_9']), 'sold'] = False
    #_df.loc[(_df['sold'] == True) & (_df['macds_12_26_9'].isnull()), 'sold'] = False
    #��������� ������� ���������� ���� �������� ����������
    #_df.loc[_df['buy'] == True, 'lasttrans'] = True
    #_df.loc[_df['sold'] == True, 'lasttrans'] = False
    #_df.loc[(_df['lasttrans'] != True) & (_df['lasttrans'] != False), 'lasttrans'] = _df['lasttrans'].shift(1)
    #_df.loc[(_df['lasttrans'] != True) & (_df['lasttrans'] != False), 'lasttrans'] = _df['lasttrans'].shift(1)
    #�� ���� ������ ������� ���� �� ������� �� ������� ������� � ������������ ������� ����� �� ��������� ���������� ���� ����� ������ ���������
    #_df.loc[(_df['lasttrans'] == _df['buy']) | (_df['lasttrans'] == _df['sold']), 'lasttrans'] = _df['lasttrans'].shift(1)
    #�� �������� ��� ��� ��� ����� �� ���� � ������� �� ���������. �����. ����� ��������� ��� � ���� ������.

    return _df

def calculateTransaction(_df):      #������� ������ (expense) � ������ (income) �� ����� ����������
    #���, ��� ��������� �����, ������� �������� ��� ���:
    #��������� ������ ������ ������� � �������
    fsi = _df[_df.sold==True].first_valid_index()
    fbi = _df[_df.buy==True].first_valid_index()
    #print ('first valid index is ', a)
    #���� ������� ���� ������ �������, �� �� ���������� ����������
    #(��� � ������� sold, �� ��� ����� �.�. ������� �� ����� �������������� �� �������, � � ���� � ������)
    #if fsi < fbi:
    #    _df.loc[_df.index == fsi, 'sold'] = np.nan
    #� ������ � ����! �� ������� sold � ��������� ������ �� ��������� ��� ���������� � ������� :
    _df.loc[_df['sold'] == True, 'income'] = _df['close']
    if fsi < fbi:
        _df.loc[_df.index == fsi, 'income'] = np.nan
    #������ �� ��������� ��������� ������� ���� �� ��� �� ���� �������, ����� ����� ������ ��������� �������:
    #���� ������� ��������� ������� � �������
    lsi = _df.iloc[::-1][_df.sold==True].first_valid_index()
    lbi = _df.iloc[::-1][_df.buy==True].first_valid_index()
    #��������� ��������� ������� �� �������� �������
    _df.loc[_df['buy'] == True, 'expense'] = _df['close']
    if lsi < lbi:
        _df.loc[_df.index == lbi, 'expense'] = np.nan
    return _df

def showPlot(_df):      # ������ ��������
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
            y=_df['close']*_df['buy'],
            marker=dict(color='#77FF77', size=8, line=dict(color='black', width=1)),
            legendgroup='2',
            name='buy'
        ), row=1, col=1
    )
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['macd_12_26_9']*_df['buy'],
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
            y=_df['close']*_df['sold'],
            marker=dict(color='#FF0000', size=8, line=dict(color='black', width=1)),
            legendgroup='2',
            name='sold'
        ), row=1, col=1
    )
    fig.append_trace(
        go.Scatter(
            mode='markers',
            x=_df.index,
            y=_df['macd_12_26_9']*_df['sold'],
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

def calcProfit (_df):   # ������� ������ �� ������� ���������� ����� ���������� ��������, ��������� � ������� ��������
    #��������� �������
    expense = _df['expense'].sum()
    #��������� �����
    income = _df['income'].sum()
    #�������
    profit = income - expense
    #������� � % �� ������
    profitPercent = round(profit/expense*100, 2)
    #��� ������� ��� ��������� ��������� ��������� � �������:
    #��� ���� �� ���� �� �� ������ ���������� ������� � ������ ������� � ������� � ����� ��� ���� ����
    passiveProfit = _df['close'][_df.index[-1]] - _df['close'][_df.index[0]]
    passiveProfitPercent = round(passiveProfit/_df['close'][_df.index[0]]*100, 2)
    #������� ��� ������
    print('expense = ', expense)
    print('income = ', income)
    print('profit = ', profit, ' (', profitPercent, '%)')
    print('passive profit = ', passiveProfit, ' (', passiveProfitPercent, '%)')

def printDf(_df, _feature=np.nan, _condition=True):   #������� ���� � �������� _condition(_feature)
    #����� ��� ��������
    if (_feature == np.nan):
        print(_df)
    else:
        print(_df[_df[_feature] == _condition])
        
    #������ ����������� ���������� � macd
    #printDf(df1, 'cross') ������������:
    #print(df1[df1['cross'] == True])

def executeAll(_df):    # ��� ��������
    _df = normalise(_df)
    _df = calculateTransaction(_df)
    calcProfit(_df)
    showPlot(_df)

#df1 - ������� MACD
#df2 - MACD � ����������� (�������� ������������ �� ���� ������)
#df3 - �������� ������� �� ��������� ���������� ����������� MACD

print("MACD calculating (df1):")
executeAll(df1)
print("MACD extremum calculating (df3):")
executeAll(df3)
#printDf(df3, 'extremum')
#print(df3.head(50))
#print(df3.tail(50))