# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:36:26 2020

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
S = 1000 # количество слотов в целом
n = 10  # количество экспериментов для усреднения
m = int(round(((a - h) / h + 1), 1))  # количество элементов в лямде
lamda = np.zeros(m)  # параметр интенсивности сообщений (Пуассоновский поток)
# массив среднего количества сообщений в буфере в алгоритме случайного
# множественного доступа. скопирован после работы программы ил ЛР1
MIN_sr_PR = np.array([1.830000000000000376e-02,
4.383333333333332832e-02,
6.590000000000000024e-02,
1.036166666666666625e-01,
1.528333333333333210e-01,
2.144000000000000072e-01,
2.773166666666666558e-01,
4.847666666666666235e-01,
7.359666666666666579e-01,
1.119366666666666621e+00,
3.384749999999999481e+00,
8.120616666666666816e+00,
9.450550000000001560e+00,
1.514734999999999943e+01,
1.790649999999999764e+01,
2.285813333333333475e+01,
2.715136666666667153e+01,
3.046109999999999829e+01,
3.531391666666665685e+01,
3.882074999999999676e+01])

# заполнение массива
for i in range(m):
    lamda[i] = round(i / m + h, 2)
    
# функция для составления расписания
# если в P1 и P2 массивы, то они должны быть numpy!!!! 
# A1, A2, A3, A4 - начальные положения решения о передаче для абонентов
# P1, P2 - начальные положения решения о передаче для ретрансляторов
# вместе составляют переиод раписания
def schedule_AB_RET(A1, A2, A3, A4, P1, P2):
    timing_AB = np.zeros([M, S]) # расписание абонентов
    timing_RET = np.zeros([N, S]) # расписание ретрансляторов
    #объденяем нач. пол. абонентов и находим максимум
    max1 = np.max(np.vstack((A1,A2,A3,A4))) 
    #объденяем нач. пол. ретрансляторов и находим максимум
    max2 = np.max(np.vstack((P1,P2)))
    # общий максимум - за сколько слотов + 1 потовряется период
    max_max = max(max1, max2) 
    # формирование расписания для абонентов
    for i in range(M):
        for j in range(S):
            if j % (max_max + 1) == 0: # кратность по слотам (период)
                if i == 0: # для первого абонента
                    timing_AB[i,A1 + j] = 1
                elif i == 1: # для второго абонента
                    timing_AB[i,A2 + j] = 1
                elif i == 2: # для третьего абонента
                    timing_AB[i,A3 + j] = 1
                elif i == 3: # для четвёртого абонента
                    timing_AB[i,A4 + j] = 1
    # формирования расписания для ретрансляторов
    for i in range(N):
        for j in range(S):
            if j % (max_max + 1) == 0: # кратность по слотам (период)
                if i == 0: # для первого ретранслятора
                    timing_RET[i,P1 + j]=1
                elif i == 1: # для второго ретранслятора
                   timing_RET[i,P2 + j]=1
    return(timing_AB, timing_RET)

# моделирование работы системы по расписанию
def system_simulation(solution_of_abr, solution_of_rbs): 
    print("Запуск")
    #переменные для расчётов
    MIN_sr = np.zeros(m) #средние значения
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
    #работа системы
    for f in range(m):
        #print("Лямда "+ str(f+1))
        minsr = 0
        for w in range(n):
            mass = np.random.poisson(lamda[f]/M , (M, S)) 
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
                # сообщения которые могут быть переданны на БС
                tr_message_RBS[:,s] = (buf_ret_start[:,s] > 0 ) * solution_of_rbs[:,s]
                # кол-во сообщение в конце слота ретраслятора =
                # сообщения которы были в начале + сообщения пришедшие
                # за текущий слот от абонентов - переданные сообщения на БС
                buf_ret_end[:,s] = buf_ret_start[:,s] + message_ABtoR[:,s] - tr_message_RBS[:,s]
                # кол-во сообщений на начало следующего слота равно
                # кол-ву сообщений в конце текущего слота
                buf_ret_start[:,s + 1] = buf_ret_end[:,s]
            #средние значение сообщений в буфере
            minsr += (sum(np.sum(buf_ab_end, axis=0)) + sum(np.sum(buf_ret_end, axis=0))) / (S * (M+N))
        # усреднение значений
        MIN_sr[f] = minsr/n
    return(MIN_sr)

# построение расписаний и расчёт среднийх значений
# оптимальное расписание
timetable_abr_optimal, timetable_rbs_optimal = schedule_AB_RET(0,1,0,1,0,1)
mean_message_optimal = system_simulation(timetable_abr_optimal, timetable_rbs_optimal)
# придуманное раписание №1
timetable_abr_my1, timetable_rbs_my1 = schedule_AB_RET(0,4,1,5,np.array([2, 6]),np.array([3, 7]))
mean_message_my1 = system_simulation(timetable_abr_my1, timetable_rbs_my1)
# придуманное расписание №2
timetable_abr_my2, timetable_rbs_my2 = schedule_AB_RET(0,1,2,3,np.array([0, 1]),np.array([2, 3]))
mean_message_my2 = system_simulation(timetable_abr_my2, timetable_rbs_my2)

### ПОСТРОЕНИЕ ГРАФИКОВ расписания и алгоритма множественного доступа
fig1 = plt.figure()
plt.grid(True, color=[0, 0, 0])
plt.title('Зависимость оценки среднего количества сообщений в системе от лямды', fontsize=15)
plt.plot(lamda, MIN_sr_PR, color = 'red', label = 'Алгоритм случайного множественного доступа')
plt.plot(lamda, mean_message_optimal, color = 'blue',linestyle = '--', label = 'Оптимальное расписание')
plt.plot(lamda, mean_message_my1, color = 'green', linestyle = '-.', label = 'Расписание №1')
plt.plot(lamda, mean_message_my2, color = [1,0,1], linestyle = ':', label = 'Расписание №2')
plt.xlabel('Интенсивность лямда')
plt.ylabel('Среднее число абонентов в буфере')
plt.legend()
'''
# придуманное расписание №1 и случайный множественный доступ
fig2 = plt.figure()
plt.grid(True, color=[0, 0, 0])
plt.title('Зависимость оценки среднего количества сообщений в системе от лямды', fontsize=15)
plt.plot(lamda, mean_message_my1, color = 'green',label = 'Расписание №1')
plt.plot(lamda, MIN_sr_PR, color = 'red', label = 'Алгоритм случайного множественного доступа')
plt.xlabel('Итенсивность лямда')
plt.ylabel('Среднее число абонентов в буфере')
plt.legend()

# придуманное расписание №2 и случайный множественный доступ
fig3 = plt.figure()
plt.grid(True, color=[0, 0, 0])
plt.title('Зависимость оценки среднего количества сообщений в системе от лямды', fontsize=15)
plt.plot(lamda, mean_message_my2, color = [1,0,1],label = 'Расписание №2')
plt.plot(lamda, MIN_sr_PR, color = 'red', label = 'Алгоритм случайного множественного доступа')
plt.xlabel('Итенсивность лямда')
plt.ylabel('Среднее число абонентов в буфере')
plt.legend()
'''