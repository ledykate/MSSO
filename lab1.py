# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 18:14:41 2020

@author: Катрина
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams  # русскоязычные подписи на графиках

rcParams['font.family'] = 'fantasy'
rcParams['font.fantasy'] = 'Times New Roman'

M = 4  # количество абонентов
h = 0.05  # шаг и начало
a = 1  # для формирования лямды (конец)
b = 0.95  # для формирования вероятностей (конец)
S = 200#1000  # количество слотов в целом
n = 2#10  # количество экспериментов для усреднения

n1 = int(round(((a - h) / h + 1), 1))  # количество элементов в лямде
n2 = int(round(((b - h) / h + 1), 1))  # количество элементов в вероятностях
lamda = [0 for i in range(n1)]  # параметр интенсивности сообщений (Пуассоновский поток)
alfa = [0 for i in range(n1)]  # лямда/M
p_ABR = [0 for i in range(n2)]  # вероятность передачи сообщения от абонента ретранслятору
p_RBS = [0 for i in range(n2)]  # вероятность передачи сообщения от ретранслятору БС

# заполнение массивов
for i in range(n1):
    if i != (n1 - 1):
        p_ABR[i] = round(i / n1 + h, 2)
        p_RBS[i] = round(i / n1 + h, 2)
    lamda[i] = round(i / n1 + h, 2)
    alfa[i] = lamda[i] / M

P_min_sr_ABR = [0 for i in range(n1)]  # вероятности АБР для минимального среднего
P_min_sr_RBS = [0 for i in range(n1)]  # вероятности РБС для минимального среднего
MIN_sr = [0 for i in range(n1)]  # минимальные средние

for f in range(n1):
    print("Лямда "+ str(f+1))
    # переменные для экспериментов
    pabs = 0
    prbs = 0
    minsr = 0
    for w in range(n):
        print("Эксперементы "+ str(w+1))
        Q = np.int32(np.zeros([M+2,S])) # количество сообщений в слоте
        Table = np.int32(np.zeros([n2, n2]))  # таблица с вероятностями среднего кол-ва сообщений
        for i in range(n2):  # проход по вероятностям АБР
            for j in range(n2):  # проход по вероятностям РБС
                mas1 = np.random.poisson(alfa[f], (M, S))  # формирования пришедших сообщений в слот размером 4 на 1000
                Q[:4, 0] = mas1[:, 0]  # первый столбец кол-ва сообщений в слоте
                P = np.int32(np.zeros([M + 2, S]))  # веротяности передачи АБР и РБС
                for s in range(1, S):  # проход по слотам
                    for t in range(M+2):  # проход по абонентам и ретрансляторам
                        if t<4: #абоненты
                            #вероятность отправки сообщения от абонента
                            P[t][s] = np.random.choice([1, 0], 1, p=[p_ABR[i], 1 - p_ABR[i]])[0] and (Q[t][s - 1]>0)
                            if t%2==0: #кратность инекса (для 0 и 2 будет проверятся вероятность со следующим абонентом)
                                #если веротности t-абонента равна единице, а вероятность t+1 абонента равна 0 - сообещние уходит,
                                Q[t][s] = mas1[t][s] + Q[t][s-1]\
                                - (P[t][s]==1 and P[t+1][s]==0 and Q[t][s-1]>0)\
                                - (P[t][s]==1 and P[t+1][s]==1 and Q[t][s-1]>0 and Q[t+1][s-1]<=0)
                            else:#кратность инекса (для 1 и 3 будет проверятся вероятность с предыдущим абонентом)
                                #если веротности t-абонента равна единице, а вероятность t-1 абонента равна 0 - сообещние уходит
                                Q[t][s] = mas1[t][s] + Q[t][s-1]\
                                - (P[t][s]==1 and P[t-1][s]==0 and Q[t][s-1]>0)\
                                - (P[t][s]==1 and P[t-1][s]==1 and Q[t][s-1]>0 and Q[t-1][s-1]<=0)
                        else: #ретрансляторы
                            #вероятность отправки сообщения от ретранслятора
                            P[t][s] = np.random.choice([1, 0], 1, p=[p_RBS[j], 1 - p_RBS[j]])[0] and (Q[t][s - 1]>0)
                            if t==4: #для первого ретранслятора
                                #первые две проверки на вероятность ухода на БС. Вторые две проверки нужны для поступления сообщения от абонента на ретранслятор (оба варианта)
                                Q[t][s] = Q[t][s-1] - (P[t][s]==1 and P[t+1][s]==0 and Q[t][s-1]>0)\
                                - (P[t][s]==1 and P[t+1][s]==1 and Q[t][s-1]>0 and Q[t+1][s-1]<=0)\
                                + (P[t-4][s]==1 and P[t-3][s]==0 and Q[t-4][s-1]>0)\
                                + (P[t-3][s]==1 and P[t-4][s]==0 and Q[t-3][s-1]>0)\
                                + (P[t-4][s]==1 and P[t-3][s]==1 and Q[t-4][s-1]>0 and Q[t-3][s-1]<=0)\
                                + (P[t-3][s]==1 and P[t-4][s]==1 and Q[t-3][s-1]>0 and Q[t-4][s-1]<=0)
                            else:
                                #первые две проверки на вероятность ухода на БС. Вторые две проверки нужны для поступления сообщения от абонента на ретранслятор (оба варианта)
                                Q[t][s] = Q[t][s-1] - (P[t][s]==1 and P[t-1][s]==0 and Q[t][s-1]>0)\
                                - (P[t][s]==1 and P[t-1][s]==1 and Q[t][s-1]>0 and Q[t-1][s-1]<=0)\
                                + (P[t-3][s]==1 and P[t-2][s]==0 and Q[t-3][s-1]>0)\
                                + (P[t-2][s]==1 and P[t-3][s]==0 and Q[t-2][s-1]>0)\
                                + (P[t-3][s]==1 and P[t-2][s]==1 and Q[t-3][s-1]>0 and Q[t-2][s-1]<=0)\
                                + (P[t-2][s]==1 and P[t-3][s]==1 and Q[t-2][s-1]>0 and Q[t-3][s-1]<=0)
                        pass                   
                Table[i][j] = sum(np.sum(Q, axis=0)) / S  # заполнение таблицы
        r, c = np.unravel_index(Table.argmin(), Table.shape)  # нахождение индексов минимального элемента
        pabs += p_ABR[r]  # нахождение вероятности АБР
        prbs += p_RBS[c]  # нахождение вероятности РБС
        minsr += Table[r][c]  # нахождение значения минимального элемента
    # усреднение значений
    P_min_sr_ABR[f] = pabs / n
    P_min_sr_RBS[f] = prbs / n
    MIN_sr[f] = minsr / n

fig1 = plt.figure()
ax1 = fig1.add_axes([0, 2.4, 1, 1])
ax1.grid(True, color=[0, 0, 0])
ax1.set_title('Зависимость оценки среднего количества сообщений в системе от лямды', fontsize=15)
ax1.plot(lamda, MIN_sr, color='blue')
ax1.set_xlabel('Итенсивность лямда')
ax1.set_ylabel('Среднее число абонентов в буфере')
fig1.savefig('gr1.png', bbox_inches='tight')

fig2 = plt.figure()
ax2 = fig2.add_axes([0, 1.2, 1, 1])
ax2.grid(True, color=[0, 0, 0])
ax2.set_title('Вероятность отправки сообщения от абонента на ретранслятор', fontsize=15)
ax2.plot(lamda, P_min_sr_ABR, color='blue')
ax2.set_xlabel('Итенсивность лямда')
ax2.set_ylabel('Вероятсноть pАБР')
fig2.savefig('gr2.png', bbox_inches='tight')

fig3 = plt.figure()
ax3 = fig3.add_axes([0, 0, 1, 1])
ax3.grid(True, color=[0, 0, 0])
ax3.set_title('Вероятность отправки сообщения от ретранслятор на базовую станцию', fontsize=15)
ax3.plot(lamda, P_min_sr_RBS, color='blue')
ax3.set_xlabel('Итенсивность лямда')
ax3.set_ylabel('Вероятсноть pРБС')
fig3.savefig('gr3.png', bbox_inches='tight')