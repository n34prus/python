# -*- coding: cp1251 -*-
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os

# настраиваем красивый вывод в консоль наших будущих данных
# cmd = 'mode 250,70'
# os.system(cmd)
pd.set_option("display.max_columns", None)
pd.set_option('display.width', 2000)

# генерация признаков по индикаторам:
# marking - разметка идеальных точек входа и выхода в сделку на основании исторических данных, можно юзать для обучения нейронок
# macd - разметка точек входа/выхода по MACD
# macdex - разметка точек входа/выхода по локальным экстремумам скользящей MACD
# trend - разметка на основании функции корелляции (выявление тренда)
def apply_indicator(_df, _method='marking', _interpolate=0):
    # первый символ в лоуеркейсе
    _df.columns = [x.lower() for x in _df.columns]
    if _interpolate:
        # давайте интерполируем значения а то заебал этот яху свечки терять
        # на линейной интерполяции кривые свеки получаются
        _deltaT = _df.shift(1).first_valid_index() - _df.first_valid_index()  # номинальный таймфрейм
        date_index = pd.date_range(start='11/30/2021 20:00', periods=48, freq='H', tz=0)
        # print("\nold indexes: ", _df.index)
        # print("\nnew indexes: ", date_index)
        _df = _df.reindex(date_index)
        _df = _df.interpolate()
    if _method == 'marking':
        # знак угла наклона
        _df['dif'] = _df['close'].diff()
        # знак угла наклона
        _df['signdif'] = _df['dif'] >= 0
        # выделяем локальные экстремумы
        _df['extremum'] = _df['signdif'].diff()
        # print(df3)
        # покупка в случае пересечения снизу
        _df['buy'] = (_df['extremum'] == True) & (_df['signdif'] == True)
        # продажа в случае пересечения сверху
        _df['sold'] = (_df['extremum'] == True) & (_df['signdif'] == False)
        # сдвигаем всё на шаг назад. ведь нам разметка нужна а она может заглянуть на одну свечку вперед :)
        _df['buy'] = _df['buy'].shift(-1)
        _df['sold'] = _df['sold'].shift(-1)
        return _df
    elif _method == 'macd':
        # вычисляем MACD: macdh это гистограмма, macds это медленный скользящий уровень, macd это macd :)
        _df.ta.macd(close='close', fast=12, slow=26, append=True)
        _df.columns = [x.lower() for x in _df.columns]
        # добавляем признак разница slow и macd
        _df['sign'] = _df['macds_12_26_9'] < _df['macd_12_26_9']
        # проверяем смену знака (тобишь пересечение графиков)
        _df['cross'] = _df['sign'].diff()
        # покупка в случае пересечения снизу
        _df['buy'] = (_df['cross'] == True) & (_df['sign'] == True)
        # продажа в случае пересечения сверху
        _df['sold'] = (_df['cross'] == True) & (_df['sign'] == False)
        return _df
    elif _method == 'macdex':
        _df.ta.macd(close='close', fast=12, slow=26, append=True)
        _df.columns = [x.lower() for x in _df.columns]
        # дифференцируем
        _df['dif'] = _df['macd_12_26_9'].diff()
        # знак угла наклона
        _df['signdif'] = _df['dif'] >= 0
        # выделяем локальные экстремумы
        _df['extremum'] = _df['signdif'].diff()
        # покупка в случае пересечения снизу
        _df['buy'] = (_df['extremum'] == True) & (_df['signdif'] == True) & (np.isnan(_df['macds_12_26_9']) == False)
        # продажа в случае пересечения сверху
        _df['sold'] = (_df['extremum'] == True) & (_df['signdif'] == False) & (np.isnan(_df['macds_12_26_9']) == False)
        return _df
    # такс немного математики. функция кореляции строит матрицу n*n кореляции двух функций.
    # мы имеем N исторических свечек. для свечей от 0 до N/2 делаем следующее: отнимаем от цены закрытия каждой свечи величину закрытия свечи 0.
    # представляем полученную шляпу в виде функции f(t) где f - полученный на предыдущем шаге результат для каждой свечки.
    # для свечей от N/2+1 до N делаем следующее: отнимаем от цены закрытия величину закрытия свечи N/2+1
    # аналогично предпредыдущему пункту получаем функцию g(t). обращаю внимание, что t должно находиться в диапазоне 0..N/2, а не N/2+1..N
    #
    # не. давайте так. берем N свечей, от всех столбцов отнимаем цену столбцов первой свечи, получаем новые признаки - дифференциалы относительно первой свечи
    # ищем максимум среди новых максимумов и минимум среди новых минимумов. сравниваем их по модулю, наибольшее берем и все наши новые признаки на него делим!
    # получаем нормализованные признаки, они все лежат в диапазоне от -1 до 1 и с ними можно работать
    # строим матрицу N*2 где первая строчка - нормализованные цены закрытия, а вторая - нули
    # строим корелляцию по нашей матрице. первый элемент будет единица, а второй - значение кореляции с флетом
    # если 1 - у нас флет, если -1 - у нас ебаное ралли, если 0 - мы в обычном тренде
    # умножаем на -1 получаем: -1 флет, 0 тренд, 1 ралли.
    # прибавляем 1 получаем: 0 флет, 0.5 тренд, 1 ралли.
    # умножаем на знак нормализованного закрытия последней свечки, получаем хороший такой индикатор от -1 (ралли вниз) до 1 (ралли вверх), 0 - горизонталка
    # реализация будет ужасной, не смотрите туда
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


def normalise(_df):  # приводим данные в удобный для отрисовки и обработки вид
    # заполняем простой значениями NaN чтобы график был адекватный
    _df.loc[_df['buy'] == False, 'buy'] = np.nan
    _df.loc[_df['sold'] == False, 'sold'] = np.nan

    # запоминаем тип последней транзакции, False если продажа и True если покупка.
    # _df.loc[(_df['sold'] == True) & np.isnull(_df['macds_12_26_9']), 'sold'] = False
    # _df.loc[(_df['sold'] == True) & (_df['macds_12_26_9'].isnull()), 'sold'] = False
    # заполняем столбец значениями типа пследней транзакции
    # _df.loc[_df['buy'] == True, 'lasttrans'] = True
    # _df.loc[_df['sold'] == True, 'lasttrans'] = False
    # _df.loc[(_df['lasttrans'] != True) & (_df['lasttrans'] != False), 'lasttrans'] = _df['lasttrans'].shift(1)
    # _df.loc[(_df['lasttrans'] != True) & (_df['lasttrans'] != False), 'lasttrans'] = _df['lasttrans'].shift(1)
    # по идее теперь неплохо было бы сделать на целевых ячейках с транзакциями сделать сдвиг по последней транзакции вниз чтобы искать дубликаты
    # _df.loc[(_df['lasttrans'] == _df['buy']) | (_df['lasttrans'] == _df['sold']), 'lasttrans'] = _df['lasttrans'].shift(1)
    # не работает так как эта шляпа не цикл а переход по итератору. сасай. потом придумаем что с этим делать.
    return _df


def calculate_transaction(_df):  # подсчет затрат (expense) и дохода (income) во время транзацкий
    # так, тут некоторая магия, которая работает вот так:
    # вычисляем индекс первой продажи и покупки
    fsi = _df[_df.sold == True].first_valid_index()
    fbi = _df[_df.buy == True].first_valid_index()
    # print ('first valid index is ', a)
    # если продажа идет раньше покупки, то не производим транзакцию
    # (тут я отменяю sold, но это плохо т.к. продажа не будет отрисовываться на графике, а я хочу её видеть)
    # if fsi < fbi:
    #    _df.loc[_df.index == fsi, 'sold'] = np.nan
    # а теперь в кучу! не трогаем sold и аккуратно просто не учитываем эту транзакцию в профите :
    _df.loc[_df['sold'] == True, 'income'] = _df['close']
    _df.loc[_df['buy'] == True, 'expense'] = _df['close']
    try:
        if fsi < fbi:
            _df.loc[_df.index == fsi, 'income'] = np.nan
        # теперь не учитывает последнюю покупку если за ней не было продажи, также чтобы профит корректно считать:
        # ищем индексы последней покупки и продажи
        lsi = _df.iloc[::-1][_df.sold == True].first_valid_index()
        lbi = _df.iloc[::-1][_df.buy == True].first_valid_index()
        # исключаем граничную покупку из расчетов профита
        if lsi < lbi:
            _df.loc[_df.index == lbi, 'expense'] = np.nan
    except Exception:
        print('cant calculate transaction')
    return _df


def show_indicator_plot(_df):  # рисуем картинки
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


def show_basic_plot(_df):  # рисуем картинки
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


def show_plot(_df, _method='marking'):  # рисуем картинки
    if _method == 'marking':
        fig = make_subplots(rows=1, cols=1)
    else:
        fig = make_subplots(rows=2, cols=1)
    # базовый график
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



def calc_profit(_df):  # выводим баланс из расчета транзакций одной катируемой единицей, результат в базовых единицах
    # суммарные затраты
    expense = _df['expense'].sum()
    # суммарный доход
    income = _df['income'].sum()
    # прибыль
    profit = income - expense
    # прибыль в % от стоимости первой покупки
    try:
        fbi = _df[_df.buy == True].first_valid_index()
        fbv = _df['close'][fbi]
        profitPercent = round(profit / fbv * 100, 2)
    except Exception:
        print('cant calculate profit')
        return
    # тут кусочек для сравнения стратегий инвестора и трейдера:
    # что было бы если бы мы купили катируемую единицу в начале периода и продали в конце без этой ебли
    passiveProfit = _df['close'][_df.index[-1]] - _df['close'][_df.index[0]]
    passiveProfitPercent = round(passiveProfit / _df['close'][_df.index[0]] * 100, 2)
    # выводим для оценки
    print('expense = ', expense)
    print('income = ', income)
    print('first buy =', fbv)
    print('profit = ', profit, ' (', profitPercent, '%)')
    print('passive profit = ', passiveProfit, ' (', passiveProfitPercent, '%)')


def print_df(_df, _feature=np.nan, _condition=True):  # выводим базу с условием _condition(_feature)
    # вывод для проверки
    if _feature == np.nan:
        print(_df)
    else:
        print(_df[_df[_feature] == _condition])

    # только пересечения скользящей с macd
    # printDf(df1, 'cross') эквивалентно:
    # print(df1[df1['cross'] == True])


def analyze_df(_df, _method='marking', _interpolate=0):  # функция верхнего уровня
    print("\nCalculating.\nMethod:", _method, "\nInterpolation:", _interpolate)
    _df = apply_indicator(_df, _method, _interpolate)
    _df = normalise(_df)
    _df = calculate_transaction(_df)
    calc_profit(_df)
    show_plot(_df, _method)


########################### MAIN CODE ##############################

### тут выбираем данные для анализа (подгружаем с Yahoo Finance)                                                                                    ###
# акции мета за последний год на дневных свечках
df = yf.Ticker('FB').history(period='1y')[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# курс
# df = yf.Ticker('ETH-BTC').history(start="2021-10-20", end="2021-11-19", interval="15m")[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# курс доллара к евро за последний год на дневных свечках
# df = yf.Ticker('EURUSD=X').history(start="2015-02-01", end="2020-01-01", interval="1d")[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# курс битка за последний год на дневных свечках
# df = yf.Ticker('BTC-USD').history(period='1y')[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# курс битка за последние два месяца на часовых свечках
# df = yf.Ticker('BTC-USD').history(start="2021-11-01", end="2021-12-11", interval="1h")[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
analyze_df(df, 'macd')

# printDf(df3, 'extremum')
# print(df3.head(50))
# print(df3.tail(50))
