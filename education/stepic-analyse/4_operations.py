import os
import requests
import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

#debug_mode hiding output
#set debug_mode to False for looking to full result
debug_mode = False

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
succ_usr = usrlog \
    .query('success == True') \
    .groupby('client', as_index=False) \
    .agg({'success':'count'}) \
    .sort_values('success', ascending=False) \
    .reset_index(drop=True)
succ_usr['is_top'] = succ_usr['success'] == succ_usr['success'][0]
if not debug_mode:
    print('\n2. ID клиентов, совершивших больше всех успешных операций:')
    print(succ_usr.query('is_top == True').sort_values('client').client.tolist())

#3. С какой платформы осуществляется наибольшее количество успешных операций?
succ_pltf = usrlog \
    .query('success == True') \
    .groupby('platform', as_index=False) \
    .agg({'success': 'count'}) \
    .sort_values('success', ascending=False) \
    .reset_index(drop=True)
succ_pltf['is_top'] = succ_pltf['success'] == succ_pltf['success'][0]
if not debug_mode:
    print('\n3. Больше всех успешных операций совершено с платформ:')
    print(succ_pltf.query('is_top == True').sort_values('platform').platform.tolist())

#4. Какую платформу предпочитают премиальные клиенты?
prem_pltf_rate = usrlog \
    .query('premium == True') \
    .groupby('platform', as_index=False) \
    .agg({'premium': 'count'}) \
    .sort_values('premium', ascending=False) \
    .reset_index(drop=True)
prem_pltf_rate['is_top'] = prem_pltf_rate['premium'] == prem_pltf_rate['premium'][0]
if not debug_mode:
    print('\n4. Премиальные клиенты предпочитают платформы:')
    print(prem_pltf_rate.query('is_top == True').sort_values('platform').platform.tolist())

#5. Визуализируйте распределение возраста клиентов в зависимости от типа клиента (премиум или нет)
#почему тайтлы криво рисуются? в документации сиборна и стековф об этом ни слова
if not debug_mode:
    ax_prem = sns.displot(data=usrlog, x='age', hue='premium', kind='kde')
    ax_prem.set(xlabel='age', ylabel='prop', title='Распределение возраста пользователей')
    plt.show()

#6. Постройте график распределения числа успешных операций
#формулировка не очень. от нас хотят увидеть сколько пользователей (y) совершили x успешных операций
if not debug_mode:
    ax_succ = sns.displot(data=usrlog.query('success == True').groupby('client', as_index=False).agg({'success': 'count'}), x='success', binwidth=1)
    ax_succ.set(xlabel='number of successes', ylabel='user count', title='Распределение количества успешных операций')
    plt.show()

#7. Визуализируйте число успешных операций, сделанных на платформе computer, в зависимости от возраста, используя sns.countplot
#(x – возраст, y – число успешных операций)
# Клиенты какого возраста совершили наибольшее количество успешных действий?
if not debug_mode:
    comp_succ = usrlog \
        .query("success == True and platform == 'computer'")
    #    .groupby('age', as_index=False) \
    #    .agg({'success': 'count'})
    #print(comp_succ)
    plt.figure(figsize=(12, 8))
    ax_age_succ = sns.countplot(data=comp_succ, x='age')
    ax_age_succ.set(xlabel='age', ylabel='operations count', title='Распределение количества успешных операций на пк')
    plt.show()

#print(usrlog)