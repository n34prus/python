import os
import requests
import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

#проверяем наличие скачанной ксвшки, если нет то докачиваем
csvfile = __file__.split(chr(92))[-1][:-2] + 'csv'
if not os.access(csvfile, os.F_OK):
    res = requests.get('https://stepik.org/media/attachments/lesson/359240/taxi_peru.csv')
    with open(csvfile, 'w') as f:
        f.write(res.text)
#print(res.text)
#taxi = pd.read_csv(r'https://stepik.org/media/attachments/lesson/359240/taxi_peru.csv', sep=';', parse_dates=['start_at', 'end_at', 'arrived_at'])

taxi = pd.read_csv(csvfile, sep=';', parse_dates=['start_at', 'end_at', 'arrived_at'])

#с какой платформы люди чаще заказывают такси
platform_stat = taxi.groupby('source', as_index=False).agg({'journey_id': 'count'}).sort_values('journey_id', ascending=False)
platform_stat['%_from_total'] = platform_stat['journey_id']/(platform_stat['journey_id'].sum())*100
platform_stat = platform_stat.rename(columns={'journey_id': 'percentage'})
#print(stat)

#распределение оценок водителей
driver_score_counts = taxi \
    .groupby('driver_score', as_index = False) \
    .agg({'journey_id': 'count'})
driver_score_counts['journey_id'] = (driver_score_counts['journey_id']/(driver_score_counts['journey_id'].sum())).mul(100).round(2)
driver_score_counts = driver_score_counts.rename(columns={'journey_id': 'percentage'})
#print(driver_score_counts)

ax_d = sns.barplot(x='driver_score', y='percentage', data=driver_score_counts, color='blue', alpha=0.5)
ax_d.set(xlabel='Driver score', ylabel='Percentage')

#распределение оценок пассажиров
rider_score_counts = taxi \
    .groupby('rider_score', as_index = False) \
    .agg({'journey_id': 'count'})
rider_score_counts['journey_id'] = (rider_score_counts['journey_id']/(rider_score_counts['journey_id'].sum())).mul(100).round(2)
rider_score_counts = rider_score_counts.rename(columns={'journey_id': 'percentage'})
print(rider_score_counts)

ax_r = sns.barplot(x='rider_score', y='percentage', data=rider_score_counts, color='yellow', alpha=0.5)
ax_r.set(xlabel='driver(blue) & rider(yellow) score', ylabel='%')
sns.despine()  # убрать часть рамки графика
#выводим обе гистограммы на экран с наложением
plt.show()

# journey_id – уникальный id поездки
# user_id – id пользователя
# driver_id – id водителя
# taxi_id – id машины
# icon – тип поездки
# start_type – тип заказа (asap, reserved, delayed)
# start_at – время начала поездки
# start_lat – исходное местоположение пользователя, широта
# start_lon – исходное местоположение пользователя, долгота
# end_at – время окончания поездки
# end_lat – итоговое местоположение, широта
# end_lon – итоговое местоположение, долгота
# end_state – состояние заказа
# driver_start_lat – исходное местоположение водителя, широта
# driver_start_lon – исходное местоположение водителя, долгота
# arrived_at – время прибытия водителя
# source – платформа, с которой сделан заказ
# driver_score – оценка водителя клиентом
# rider_score – оценка клиента водителем