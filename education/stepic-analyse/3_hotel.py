#
import os
import requests
import pandas as pd
from datetime import datetime

#debug_mode hiding output
#set debug_mode to False for looking to full result
debug_mode = False

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 20)

# замена всех пробелов в названиях столбцов на _
def replace_spaces(_df):
    new_col_name = ''
    for old_col_name in _df.columns:
        new_col_name = old_col_name.replace(' ', '_')
        if old_col_name != new_col_name:
            _df = _df.rename(columns={old_col_name: new_col_name})
    return _df

# все столбцы в нижний регистр
def replace_uppers(_df):
    new_col_name = ''
    for old_col_name in _df.columns:
        new_col_name = old_col_name.lower()
        if old_col_name != new_col_name:
            _df = _df.rename(columns={old_col_name: new_col_name})
    return _df

#0. Подготовка данных (не выводится)
# Загрузите датасет bookings.csv с разделителем ;.
# Проверьте размер таблицы, типы переменных, а затем выведите первые 7 строк, чтобы посмотреть на данные.
# Приведите названия колонок к нижнему регистру и замените пробелы на знак нижнего подчеркивания.

#проверяем наличие скачанной ксвшки, если нет то докачиваем
csvfile = __file__.split(chr(92))[-1][:-2] + 'csv'
if not os.access(csvfile, os.F_OK):
    res = requests.get('https://stepik.org/media/attachments/lesson/360344/bookings.csv')
    with open(csvfile, 'w') as f:
        f.write(res.text)
#print(res.text)

bookings = pd.read_csv(csvfile, sep=';')
#print(bookings.dtypes.value_counts())

#нормализация столбцов (специально разными функциями, так задумано)
bookings = replace_spaces(bookings)
bookings = replace_uppers(bookings)
#print(bookings)

#1. Пользователи из каких стран совершили наибольшее число успешных бронирований? Укажите топ-5.
sucsess_rate = bookings \
    .query('is_canceled == 0') \
    .groupby('country', as_index=False) \
    .agg({'is_canceled': 'count'}) \
    .sort_values('is_canceled', ascending=False)
sucsess_rate = sucsess_rate.rename(columns={'is_canceled': 'is_sucsess'})
sucsess_rate = sucsess_rate.reset_index(drop=True)
if not debug_mode:
    print('\n1. Страны с наибольшим чисом успешных бронирований:\n', sucsess_rate.head(5))

#2. На сколько ночей в среднем бронируют отели разных типов? точность 2 знака
ch_rh_mean = bookings \
    .groupby('hotel', as_index=False) \
    .agg({'stays_total_nights': 'mean'}) \
    .round(2)
ch_rh_mean = ch_rh_mean.rename(columns={'stays_total_nights': 'stays_mean_nights'})
if not debug_mode:
    print('\n2. Средняя длительность брони для разных типов отелей:\n', ch_rh_mean)

#3. Иногда тип номера, полученного клиентом (assigned_room_type), отличается от изначально забронированного (reserved_room_type).
# Такое может произойти, например, по причине овербукинга. Сколько подобных наблюдений встретилось в датасете?
overbooking = bookings.query('assigned_room_type != reserved_room_type').shape[0]
if not debug_mode:
    print('\n3. Количество случаев заселения клиента в тип номера, отличный от забронированного: {} ({}%)'.format(overbooking, round(overbooking/bookings.shape[0], 2)))

#4. На какой месяц чаще всего успешно оформляли бронь в 2016? Изменился ли самый популярный месяц в 2017?
#слишком частный пример. лучше сразу написать код для всех годов в датасете
#статистика по месяцам всех лет:
month_rate = bookings \
    .query('is_canceled == 0') \
    .groupby(['arrival_date_month', 'arrival_date_year'], as_index=False) \
    .agg({'is_canceled': 'count'}) \
    .sort_values('is_canceled', ascending=False)
month_rate = month_rate.rename(columns={'is_canceled': 'is_sucsess'})
#print(month_rate)
#выделяем самый активный месяц в году
month_rate = month_rate \
    .groupby(['arrival_date_year'], as_index=False) \
    .agg({'is_sucsess': 'max', 'arrival_date_month': 'first'}) \
    .sort_values('arrival_date_year', ascending=False)
month_rate = month_rate.reset_index(drop=True)

#четко отвечаем на поставленные вопросы
answer421 = ''
answer422 = ''
fvi2016 = month_rate[month_rate.arrival_date_year==2016].first_valid_index()
fvi2017 = month_rate[month_rate.arrival_date_year==2017].first_valid_index()
if (month_rate['arrival_date_month'][fvi2016] == month_rate['arrival_date_month'][fvi2017]):
    answer421 = 'не '
else:
    answer422 = 'на: {}'.format(month_rate['arrival_date_month'][fvi2017])
if not debug_mode:
    print('\n4. Самые популярные месяцы в разные годы:\n', month_rate)
    print('\n4.1 Самый популярный месяц в 2016: ', month_rate['arrival_date_month'][fvi2016])
    print(f'4.2 Самый популярный месяц в 2017 {answer421}изменился {answer422}')

#5. На какой месяц бронирования отеля типа City Hotel отменялись чаще всего в каждый из годов?
#теперь группируем по отказам
month_cancel_rate = bookings \
    .query("is_canceled == 1 and hotel == 'City Hotel'") \
    .groupby(['arrival_date_month', 'arrival_date_year'], as_index=False) \
    .agg({'is_canceled': 'count'}) \
    .sort_values('is_canceled', ascending=False)
month_cancel_rate = month_cancel_rate \
    .groupby(['arrival_date_year'], as_index=False) \
    .agg({'is_canceled': 'max', 'arrival_date_month': 'first'}) \
    .sort_values('arrival_date_year', ascending=False)
month_cancel_rate = month_cancel_rate.reset_index(drop=True)
if not debug_mode:
    print('\n5. Самые "отмеяемые" месяцы для CityHotel в разные годы:\n', month_cancel_rate)

#6. Посмотрите на числовые характеристики трёх переменных: adults, children и babies. Какая из них имеет наибольшее среднее значение?
#тут делаем агрегирование, функцию запиливаем в виде листа чтобы была таблица с подписями. транспонируем, сортируем
age_mean = bookings \
    .agg({'adults': ['mean'], 'children': ['mean'], 'babies': ['mean']}) \
    .T \
    .sort_values('mean', ascending=False)
if not debug_mode:
    print('\n6. Средние значения для брони по возрасту клиента:\n', age_mean)
    print('\n6.1 Чаще всего заселяются: ', age_mean.first_valid_index())

#7. Создайте колонку total_kids, объединив children и babies. Отели какого типа в среднем пользуются большей популярностью у клиентов с детьми?
bookings['total_kids'] = bookings['children'] + bookings['babies']
kids_rate = bookings \
    .groupby(['hotel'], as_index=False) \
    .agg({'total_kids': 'mean'}) \
    .sort_values('total_kids', ascending=False)
kids_rate = kids_rate.rename(columns={'total_kids': 'mean_kids'})
kids_rate = kids_rate.reset_index(drop=True)
if not debug_mode:
    print('\n7. Детей чаще заселяют в отель типа {}'.format(kids_rate['hotel'][0]))
    print('7.1 Для этих отелей среднее количество детей на бронь составлет {} штук'.format(kids_rate['mean_kids'][0].round(2)))

#8. Создайте колонку has_kids, сравните % оттока клиентов в двух группах: с детьми и без
bookings['has_kids'] = bookings['total_kids'] > 0
churn_rate = bookings \
    .groupby(['has_kids'], as_index=False) \
    .agg({'is_canceled': 'mean'}) \
    .sort_values('is_canceled', ascending=False)
if churn_rate['has_kids'][0] == True:
    _result = 'с детьми'
else:
    _result = 'без детей'
if not debug_mode:
    print('\n8. Отток выше у клиентов {}.'.format(_result))
    print('8.1 Для этих клиентов отток составлет {}%\n'.format((churn_rate['is_canceled'][0]*100).round(2)))

