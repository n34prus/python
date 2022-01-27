# -*- coding: cp1251 -*-
import os
import requests
import pandas as pd

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




#print(bookings)

