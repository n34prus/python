# -*- coding: cp1251 -*-
import os
import requests
import pandas as pd

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 20)

#проверяем наличие скачанной ксвшки, если нет то докачиваем
csvfile = '2_taxi_nyc.csv'
if not os.access(csvfile, os.F_OK):
    res = requests.get('https://stepik.org/media/attachments/lesson/360340/' + csvfile)
    with open(csvfile, 'w') as f:
        f.write(res.text)
#print(res.text)

#taxi = pd.read_csv(r'https://stepik.org/media/attachments/lesson/360340/2_taxi_nyc.csv')
taxi = pd.read_csv(csvfile)

# заменим все пробелы в названиях столбцов на _
new_col_name = ''
for old_col_name in taxi.columns:
    new_col_name = old_col_name.replace(' ', '_')
    if old_col_name != new_col_name:
        taxi = taxi.rename(columns={old_col_name: new_col_name})
        # print('old: {} | new: {}'.format(old_col_name, new_col_name))

# распределение заказов по районам
borough_rate = taxi \
    .groupby('borough', as_index=False) \
    .agg({'pickups': sum}) \
    .sort_values('pickups', ascending=False)
# print(borough_rate)
# запоминаем самый непопулярный район
min_pickups = borough_rate.borough.iloc[-1]

# выбираем районы, из которых по праздникам (в среднем) поступает больше заказов, чем в обычные дни (тоже в среднем)
holiday_borrow_rate = taxi \
    .groupby(['borough', 'hday'], as_index=False) \
    .agg({'pickups': 'mean'}) \
    .sort_values('borough', ascending=True)
holiday_borrow_rate = holiday_borrow_rate.rename(columns={'pickups': 'mean_activity'})
holiday_borrow_rate['wday_activity'] = holiday_borrow_rate['mean_activity'] * (holiday_borrow_rate['hday'] == 'N')
holiday_borrow_rate['hday_activity'] = holiday_borrow_rate['mean_activity'] * (holiday_borrow_rate['hday'] == 'Y')
holiday_borrow_rate = holiday_borrow_rate.drop(columns=['mean_activity', 'hday'], axis=1)
holiday_borrow_rate = holiday_borrow_rate \
    .groupby('borough', as_index=False) \
    .agg({'wday_activity': sum, 'hday_activity': sum}) \
    .sort_values('borough', ascending=False)
holiday_borrow_rate['hday_dominate'] = holiday_borrow_rate['hday_activity'] > holiday_borrow_rate['wday_activity']
#print(holiday_borrow_rate)

# сколько поездок было по месяцам в каждом районе
pickups_by_mon_bor = taxi \
    .groupby(['pickup_month', 'borough'], as_index=False) \
    .agg({'pickups': sum}) \
    .sort_values('pickups', ascending=False)
pickups_by_mon_bor = pickups_by_mon_bor.reset_index(drop=True)
#print(pickups_by_mon_bor)

# добавить температуру в градусах цельсия
def temp_to_celcius(temp_F):
    return (temp_F - 32)*5.0/9.0

taxi['temp_C'] = temp_to_celcius(taxi['temp'])

# print(taxi.pickups.sum())
print(taxi)
