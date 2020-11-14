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

n1 = int(round(((a - h) / h + 1), 1))  # количество элементов в лямде
lamda = [0 for i in range(n1)]  # параметр интенсивности сообщений (Пуассоновский поток)
alfa = [0 for i in range(n1)]  # лямда/M

# заполнение массивов
for i in range(n1):
    lamda[i] = round(i / n1 + h, 2)
    alfa[i] = lamda[i] / M
    
lamda1 = [0 for i in range(20)]  # параметр интенсивности сообщений (Пуассоновский поток)

# заполнение массивов
for i in range(20):
    lamda1[i] = round(i / n1 + h, 2)
    
    
# если в P1 и P2 массивы, то они должны быть numpy!!!! 
def schedule_AB_RET(A1, A2, A3, A4, P1, P2):
    timing_AB = np.zeros([M, S])
    timing_RET = np.zeros([N, S])
    max1 = np.max(np.vstack((A1,A2,A3,A4)))
    max2 = np.max(np.vstack((P1,P2)))
    max_max = max(max1, max2)
    for i in range(M):
        for j in range(S):
            if j % (max_max + 1) == 0:
                if i == 0:
                    timing_AB[i,A1 + j] = 1
                elif i == 1:
                    timing_AB[i,A2 + j] = 1
                elif i == 2:
                    timing_AB[i,A3 + j] = 1
                elif i == 3:
                    timing_AB[i,A4 + j] = 1
    for i in range(M):
        for j in range(S):
            if j % (max_max + 1) == 0:
                if i == 0:
                    timing_RET[i,P1 + j]=1
                elif i == 1:
                   timing_RET[i,P2 + j]=1
    return(timing_AB, timing_RET)
    
MIN_sr = [0 for i in range(n1)] # минимальные средние из таблицы
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

MIN_sr = np.zeros(n1) #средние значения

for f in range(n1):
    print("Лямда "+ str(f+1))
    minsr = 0
    #Table[:,:]=0
    for w in range(n):
        mass = np.random.poisson(alfa[f], (M, S)) 
        solution_of_abr, solution_of_rbs = schedule_AB_RET(0,1,0,1,0,1)
        #solution_of_abr, solution_of_rbs = schedule_AB_RET(0,4,1,5,np.array([2, 6]),np.array([3, 7]))
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
        minsr += (sum(np.sum(buf_ab_end, axis=0)) + sum(np.sum(buf_ret_end, axis=0))) / (S * (M+N))
    # усреднение значений
    MIN_sr[f] = minsr/n
    
    
### ПОСТРОЕНИЕ ГРАФИКОВ
fig1 = plt.figure()
#ax1 = fig1.add_axes([0, 2.4, 1, 1])
plt.grid(True, color=[0, 0, 0])
plt.title('Зависимость оценки среднего количества сообщений в системе от лямды', fontsize=15)
plt.plot(lamda, MIN_sr, color = 'blue')
plt.plot(lamda1, MIN_sr_PR, color = 'red')
plt.xlabel('Итенсивность лямда')
plt.ylabel('Среднее число абонентов в буфере')
#fig1.savefig('graf1.png', bbox_inches='tight')

'''
A1 = 0
A2 = 1
A3 = 0
A4 = 1
P1 = 0
P2 = 1
max1 = np.max(np.vstack((A1,A2,A3,A4)))
max2 = np.max(np.vstack((P1,P2)))
max_max = max(max1,max2)
for i in range(M):
    for j in range(S):
        if j % (max_max+1) == 0:
            if i == 0:
                timetable_AB[i,A1+j] = 1
            if i == 1:
                timetable_AB[i,A2+j] = 1
            if i == 2:
                timetable_AB[i,A3+j] = 1
            if i == 3:
                timetable_AB[i,A4+j] = 1
for i in range(M):
    for j in range(S):
        if j % (max_max+1) == 0:
            if i == 0:
                timetable_RET[i,P1+j]=1
            if i == 1:
                timetable_RET[i,P2+j]=1


timetable_AB1 = np.zeros([M,S])
timetable_RET1 = np.zeros([N,S])            
A1 = 0
A2 = 4
A3 = 1
A4 = 5
P1 = np.array([2, 6])
P2 = np.array([3,7])
max1 = np.max(np.vstack((A1,A2,A3,A4)))
max2 = np.max(np.vstack((P1,P2)))
max_max = max(max1,max2)

for i in range(M):
    for j in range(S):
        if j % (max_max+1) == 0:
            if i == 0:
                timetable_AB1[i,A1+j] = 1
            if i == 1:
                timetable_AB1[i,A2+j] = 1
            if i == 2:
                timetable_AB1[i,A3+j] = 1
            if i == 3:
                timetable_AB1[i,A4+j] = 1
for i in range(M):
    for j in range(S):
        if j % (max_max+1) == 0:
            if i == 0:
                timetable_RET1[i,P1+j]=1
            if i == 1:
                timetable_RET1[i,P2+j]=1
                
                
for i in range(M):
    for j in range(S):
        if j % 2 == 0 and (i == 0 or i == 2):
            timetable_AB[i,j] = 1
        elif j % 2 == 1 and (i == 1 or i == 3):
            timetable_AB[i,j] = 1
for i in range(N):
    for j in range(S):
        if j % 2 == 0 and i == 0:
            timetable_RET[i,j] = 1
        elif j % 2 == 1 and i == 1:
            timetable_RET[i,j] = 1
'''