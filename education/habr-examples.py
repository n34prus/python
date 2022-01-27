# -*- coding: cp1251 -*-
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pylab import rcParams
sns.set()
rcParams['figure.figsize'] = 10, 6
#config InlineBackend.figure_format = 'svg'
np.random.seed(42)

x1 = np.array([7.68,5.40,3.99,3.27,2.70,5.85,6.53,5.00,4.60,6.18])
x2 = np.array([1.33,1.66,2.76,4.56,4.75,0.70,3.13,1.96,4.60,3.69])

plt.bar(np.arange(10) - 0.2, x1, width=0.4, label='До')
plt.bar(np.arange(10) + 0.2, x2, width=0.4, label='После')
plt.xticks(np.arange(10))
plt.legend()
plt.title('Изменение метрики качества (чем меньше - тем лучше)',
          fontsize=15)
plt.xlabel('id работника', fontsize=15)
plt.ylabel('Дельта');

#частотное распределение
sns_plot = sns.histplot(x1, x=x2)
fig = sns_plot.get_figure()
fig.show()

# plt.show()

# вычисляем t-student test для зависимых выборок:
# print(stats.ttest_rel(x2, x1))

# выводим среднее и стандартное отклонение

# print(f'mean(x1) = {x1.mean():.3}')
# print(f'mean(x2) = {x2.mean():.3}')
# print('-'*15)
# print(f'std(x1) = {x1.std(ddof=1):.3}')
# print(f'std(x2) = {x2.std(ddof=1):.3}')

# однофакторный дисперсионный анализ
# чем меньше значение pvalue, тем меньше вероятность того, что средние генеральных совокупностей равны
# print(stats.f_oneway(x1, x2))

print('calc: ', 0.95**8)