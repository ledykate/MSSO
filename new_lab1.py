# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 19:29:34 2020

@author: Катрина
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams  # русскоязычные подписи на графиках

rcParams['font.family'] = 'fantasy'
rcParams['font.fantasy'] = 'Times New Roman'

M = 4  # количество абонентов
N = 2 # количество ретрансляторов
h = 0.05  # шаг и начало
a = 1  # для формирования лямды (конец)
b = 0.95  # для формирования вероятностей (конец)
S = 1000 # количество слотов в целом
n = 10  # количество экспериментов для усреднения

n1 = int(round(((a - h) / h + 1), 1))  # количество элементов в лямде
n2 = int(round(((b - h) / h + 1), 1))  # количество элементов в вероятностях
lamda = [0 for i in range(n1)]  # параметр интенсивности сообщений (Пуассоновский поток)
alfa = [0 for i in range(n1)]  # лямда/M
Pr = [0 for i in range(n2)]  # вероятность передачи сообщения

# заполнение массивов
for i in range(n1):
    if i != (n1 - 1):
        Pr[i] = round(i / n1 + h, 2)
    lamda[i] = round(i / n1 + h, 2)
    alfa[i] = lamda[i] / M

# количество сообщений, находящиеся в начале слота для ретранслятора
buf_ret_start = np.zeros([N,S+1]) 
# количество сообщений, находящиеся в конце слота для ретранслятора
buf_ret_end = np.zeros([N,S]) 
# количество сообщений, находящиеся в начале слота для каждого абонента
buf_ab_start = np.zeros([M,S+1]) 
# количество сообщений, находящиеся в конце слота для каждого абонента
buf_ab_end = np.zeros([M,S]) 
# сообещния, которые могут передаться без конфликта от ретанслятора
tr_message_RBS = np.zeros([N,S]) 
# сообещния, которые могут передаться без конфликта от абонентов
tr_message_ABR = np.zeros([M,S]) 
message_ABtoR = np.zeros([N,S]) # переданные сообещения
Table = np.zeros([n2, n2]) #таблица с вероятностями

# вероятности передачи сообщения от абонента для минимального среднего
P_min_sr_ABR = [0 for i in range(n1)]  
# вероятности передачи сообщения от рентралятора для минимального среднего
P_min_sr_RBS = [0 for i in range(n1)] 
MIN_sr = [0 for i in range(n1)] # минимальные средние из таблицы

for f in range(n1):
    print("Лямда "+ str(f+1))
    # переменные для усреднения
    pabs = 0
    prbs = 0
    minsr = 0
    for w in range(n):
        print(w)
        Table[:, :] = 0 # обнуление таблицы
        # формирования пришедших сообщений от абонентов в слот
        mass = np.random.poisson(alfa[f], (M, S)) 
        for i in range(n2):
            # решение о передаче сообщения от абонента
            solution_of_abr = np.random.choice([1, 0], (M,S), p=[Pr[i], 1 - Pr[i]]) 
            for j in range(n2):
                # решение о передачи сообщения от рентранслятора
                solution_of_rbs = np.random.choice([1, 0], (N,S), p=[Pr[j], 1 - Pr[j]]) 
                # обнуление переменных
                tr_message_RBS[:, :] = 0
                tr_message_ABR[:, :] = 0
                buf_ret_start[:, :] = 0
                buf_ret_end[:,:] = 0
                buf_ab_start[:,:] = 0
                buf_ab_end[:,:] = 0
                for s in range(S):
                    # сообщения которые могут быть переданны от абонентов
                    tr_message_ABR[:, s] = (buf_ab_start[:, s] > 0 ) * solution_of_abr[:, s] 
                    # проверка на конфликты для абонентов при передаче на ретраснлятор
                    for t in range(2,5,2):
                        Flag = sum(tr_message_ABR[(t-2):t,s]) #для проверки конфликта
                        if Flag < 2: # если меньше 2, то конфликт остутсвует
                            # кол-во сообщение в конце слота абонента =
                            # сообщения которы были в начале + сообщения пришедшие
                            # за текущий слот - переданные сообщения
                            buf_ab_end[(t-2):t,s] = buf_ab_start[(t-2):t,s] + mass[(t-2):t,s] - tr_message_ABR[(t-2):t,s]
                            # кол-во сообщений на начало следующего слота =
                            # кол-ву сообщений в конце текущего слота
                            buf_ab_start[(t-2):t,s + 1] = buf_ab_end[(t-2):t,s]
                            # формируем сообщения, которые будут отправлены на 
                            # ретранслятор (т.е. 0 или 1)
                            message_ABtoR[round(t/2)-1,s] = Flag
                        else: # имеется конфликт. ничего не изменяем, не отправлем
                            # кол-во сообщение в конце слота абонента =
                            # сообщения которы были в начале + сообщения пришедшие
                            # за текущий слот
                            buf_ab_end[(t-2):t,s] = buf_ab_start[(t-2):t,s] + mass[(t-2):t,s]
                            # кол-во сообщений на начало следующего слота равно
                            # кол-ву сообщений в конце текущего слота
                            buf_ab_start[(t-2):t,s + 1] =  buf_ab_end[(t-2):t,s]
                            # на ретранлятор ничего не будет отправлено, поэтому 0
                            message_ABtoR[round(t/2)-1,s] = 0
                    # сообщения которые могут быть переданны на БС
                    tr_message_RBS[:,s] = (buf_ret_start[:,s] > 0 ) * solution_of_rbs[:,s]
                    Flag1 =  sum(tr_message_RBS[:,s]) # проверка конфликта 
                    if Flag1 < 2: # меньше 2, то конфликта нет
                        # кол-во сообщение в конце слота ретраслятора =
                        # сообщения которы были в начале + сообщения пришедшие
                        # за текущий слот от абонентов - переданные сообщения на БС
                        buf_ret_end[:,s] = buf_ret_start[:,s] + message_ABtoR[:,s] - tr_message_RBS[:,s]
                        # кол-во сообщений на начало следующего слота равно
                        # кол-ву сообщений в конце текущего слота
                        buf_ret_start[:,s + 1] = buf_ret_end[:,s]
                    else: #есть конфликт
                        # кол-во сообщение в конце слота ретраслятора =
                        # сообщения которы были в начале + сообщения пришедшие
                        # за текущий слот от абонентов
                        buf_ret_end[:,s] = buf_ret_start[:,s] + message_ABtoR[:,s]
                        # кол-во сообщений на начало следующего слота равно
                        # кол-ву сообщений в конце текущего слота
                        buf_ret_start[:,s + 1] = buf_ret_end[:,s]
                # заполнение таблицы
                Table[i][j] = (sum(np.sum(buf_ab_end, axis=0)) + sum(np.sum(buf_ret_end, axis=0))) / (S * (M+N))
        r, c = np.unravel_index(Table.argmin(), Table.shape)  # нахождение индексов минимального элемента
        pabs += Pr[r]  # нахождение вероятности АБР
        prbs += Pr[c]  # нахождение вероятности РБС
        minsr += np.min(Table)  # нахождение значения минимального элемента
    # усреднение значений
    P_min_sr_ABR[f] = pabs / n
    P_min_sr_RBS[f] = prbs / n
    MIN_sr[f] = minsr / n

### ПОСТРОЕНИЕ ГРАФИКОВ
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