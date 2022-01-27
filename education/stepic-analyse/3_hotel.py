# -*- coding: cp1251 -*-
import os
import requests
import pandas as pd
from datetime import datetime

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 20)

# ������ ���� �������� � ��������� �������� �� _
def replace_spaces(_df):
    new_col_name = ''
    for old_col_name in _df.columns:
        new_col_name = old_col_name.replace(' ', '_')
        if old_col_name != new_col_name:
            _df = _df.rename(columns={old_col_name: new_col_name})
    return _df

# ��� ������� � ������ �������
def replace_uppers(_df):
    new_col_name = ''
    for old_col_name in _df.columns:
        new_col_name = old_col_name.lower()
        if old_col_name != new_col_name:
            _df = _df.rename(columns={old_col_name: new_col_name})
    return _df

#0. ���������� ������ (�� ���������)
# ��������� ������� bookings.csv � ������������ ;.
# ��������� ������ �������, ���� ����������, � ����� �������� ������ 7 �����, ����� ���������� �� ������.
# ��������� �������� ������� � ������� �������� � �������� ������� �� ���� ������� �������������.

#��������� ������� ��������� ������, ���� ��� �� ����������
csvfile = 'bookings.csv'
if not os.access(csvfile, os.F_OK):
    res = requests.get('https://stepik.org/media/attachments/lesson/360344/' + csvfile)
    with open(csvfile, 'w') as f:
        f.write(res.text)
#print(res.text)

bookings = pd.read_csv(csvfile, sep=';')
#print(bookings.dtypes.value_counts())

#������������ �������� (���������� ������� ���������, ��� ��������)
bookings = replace_spaces(bookings)
bookings = replace_uppers(bookings)
#print(bookings)

#1. ������������ �� ����� ����� ��������� ���������� ����� �������� ������������? ������� ���-5.
sucsess_rate = bookings \
    .query('is_canceled == 0') \
    .groupby('country', as_index=False) \
    .agg({'is_canceled': 'count'}) \
    .sort_values('is_canceled', ascending=False)
sucsess_rate = sucsess_rate.rename(columns={'is_canceled': 'is_sucsess'})
sucsess_rate = sucsess_rate.reset_index(drop=True)
#print('\n1. ������ � ���������� ����� �������� ������������:\n', sucsess_rate.head(5))

#2. �� ������� ����� � ������� ��������� ����� ������ �����? �������� 2 �����
ch_rh_mean = bookings \
    .groupby('hotel', as_index=False) \
    .agg({'stays_total_nights': 'mean'}) \
    .round(2)
ch_rh_mean = ch_rh_mean.rename(columns={'stays_total_nights': 'stays_mean_nights'})
#print('\n2. ������� ������������ ����� ��� ������ ����� ������:\n', ch_rh_mean)

#3. ������ ��� ������, ����������� �������� (assigned_room_type), ���������� �� ���������� ���������������� (reserved_room_type).
# ����� ����� ���������, ��������, �� ������� �����������. ������� �������� ���������� ����������� � ��������?
overbooking = bookings.query('assigned_room_type != reserved_room_type').shape[0]
#print('\n3. ���������� ������� ��������� ������� � ��� ������, �������� �� ����������������: {} ({}%)'.format(overbooking, round(overbooking/bookings.shape[0], 2)))

#4. �� ����� ����� ���� ����� ������� ��������� ����� � 2016? ��������� �� ����� ���������� ����� � 2017?
#������� ������� ������. ����� ����� �������� ��� ��� ���� ����� � ��������
#���������� �� ������� ���� ���:
month_rate = bookings \
    .query('is_canceled == 0') \
    .groupby(['arrival_date_month', 'arrival_date_year'], as_index=False) \
    .agg({'is_canceled': 'count'}) \
    .sort_values('is_canceled', ascending=False)
month_rate = month_rate.rename(columns={'is_canceled': 'is_sucsess'})
#print(month_rate)
#�������� ����� �������� ����� � ����
month_rate = month_rate \
    .groupby(['arrival_date_year'], as_index=False) \
    .agg({'is_sucsess': 'max', 'arrival_date_month': 'first'}) \
    .sort_values('arrival_date_year', ascending=False)
month_rate = month_rate.reset_index(drop=True)

#����� �������� �� ������������ �������
answer421 = ''
answer422 = ''
fvi2016 = month_rate[month_rate.arrival_date_year==2016].first_valid_index()
fvi2017 = month_rate[month_rate.arrival_date_year==2017].first_valid_index()
if (month_rate['arrival_date_month'][fvi2016] == month_rate['arrival_date_month'][fvi2017]):
    answer421 = '�� '
else:
    answer422 = '��: {}'.format(month_rate['arrival_date_month'][fvi2017])
print('\n4. ����� ���������� ������ � ������ ����:\n', month_rate)
print('\n4.1 ����� ���������� ����� � 2016: ', month_rate['arrival_date_month'][fvi2016])
print(f'4.2 ����� ���������� ����� � 2017 {answer421}��������� {answer422}')
#print(bookings)

