#
import os
import requests
import pandas as pd
from datetime import datetime

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
csvfile = 'bookings.csv'
if not os.access(csvfile, os.F_OK):
    res = requests.get('https://stepik.org/media/attachments/lesson/360344/' + csvfile)
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
#print('\n1. Страны с наибольшим чисом успешных бронирований:\n', sucsess_rate.head(5))

#2. На сколько ночей в среднем бронируют отели разных типов? точность 2 знака
ch_rh_mean = bookings \
    .groupby('hotel', as_index=False) \
    .agg({'stays_total_nights': 'mean'}) \
    .round(2)
ch_rh_mean = ch_rh_mean.rename(columns={'stays_total_nights': 'stays_mean_nights'})
#print('\n2. Средняя длительность брони для разных типов отелей:\n', ch_rh_mean)

#3. Иногда тип номера, полученного клиентом (assigned_room_type), отличается от изначально забронированного (reserved_room_type).
# Такое может произойти, например, по причине овербукинга. Сколько подобных наблюдений встретилось в датасете?
overbooking = bookings.query('assigned_room_type != reserved_room_type').shape[0]
#print('\n3. Количество случаев заселения клиента в тип номера, отличный от забронированного: {} ({}%)'.format(overbooking, round(overbooking/bookings.shape[0], 2)))

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
print('\n4. Самые популярные месяцы в разные годы:\n', month_rate)
print('\n4.1 Самый популярный месяц в 2016: ', month_rate['arrival_date_month'][fvi2016])
print(f'4.2 Самый популярный месяц в 2017 {answer421}изменился {answer422}')
#print(bookings)

