import os
import requests
import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

#debug_mode hiding output
#set debug_mode to False for looking to full result
debug_mode = True

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 20)

# загружает датасет если его нет, называет также как скрипт и кидает рядом с ним
# аргументы - ссылка и постфикс на случай если несколько датасетов надо
# возвращает название csv
def download_csv(_url, _postfix=''):
    csvname = __file__.split(chr(92))[-1][:-3] + _postfix + '.csv'
    if not os.access(csvname, os.F_OK):
        res = requests.get(_url)
        with open(csvname, 'w') as f:
            f.write(res.text)
    return csvname

#1. Загрузите два датасета user_data и logs. Проверьте размер таблицы, типы переменных, наличие пропущенных значений, описательную статистику.

usr = pd.read_csv(download_csv('https://stepik.org/media/attachments/lesson/360348/user_data.csv', '_usr'))
log = pd.read_csv(download_csv('https://stepik.org/media/attachments/lesson/360348/logs.csv', '_log'))
#в логах время в формате unix. надо в дейттайм конвертнуть пожалуй
log['datetime'] = pd.to_datetime(log.time, unit='s')

#глянем общую инфу о датасетах
def df_diag(_df):
    print('\nРазмер:', _df.shape)
    print('\nТипы:\n', _df.dtypes)
    print('\nОписание:\n', _df.describe())
    print('\nУникальные:\n', _df.nunique())
    print('\nПустые:')
    print(_df.info())

#df_diag(usr)
#df_diag(log)
#всё ок можно мержить. берем только логи об известных пользователях
usrlog = usr.merge(log, how='inner', on='client')
if not debug_mode:
    print('\n1. Описание итогового датафрейма:')
    print(df_diag(usrlog))

#2. Какой клиент совершил больше всего успешных операций?
succ_count = usrlog \
    .query('success == True') \
    .groupby('client', as_index=False) \
    .agg({'success':'count'}) \
    .sort_values('success', ascending=False) \
    .reset_index(drop=True)
succ_count['is_top'] = succ_count['success'] == succ_count['success'][0]
if not debug_mode:
    print('\n2. ID клиентов, совершивших больше всех успешных операций:')
    print(succ_count.query('is_top == True').sort_values('client').client.tolist())

