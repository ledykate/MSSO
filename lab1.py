# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 18:14:41 2020

@author: Катрина
"""

import numpy as np
import random
import matplotlib.pyplot as plt 
from matplotlib import rcParams #русскоязычные подписи на графиках 
rcParams['font.family']='fantasy' 
rcParams['font.fantasy']='Times New Roman'

M = 4 #количество абонентов
h = 0.05 #шаг и начало
a = 1 #для формирования лямды (конец)
b = 0.95 #для формирования вероятностей (конец)
S = 1000 #количество слотов в целом
n = 10 #количество эксперементов для усреднения

n1 = int(round(((a-h)/h+1),1)) #количество элементов в лямде
n2 = int(round(((b-h)/h+1),1)) #количество элементов в вероятностях
lamda = [0 for i in range(n1)] #параметр интенсивности сообщений (Пуассоновский поток)
alfa = [0 for i in range(n1)] #лямда/M
p_ABR = [0 for i in range(n2)] #вероятность передачи сообщения от абонента ретранслятору
p_RBS = [0 for i in range(n2)] #вероятность передачи сообщения от ретранслятору БС

#заполнение массивов
for i in range(n1):
    if i!=(n1-1):
        p_ABR[i] = round(i/n1+h,2)
        p_RBS[i] = round(i/n1+h,2)
    lamda[i] = round(i/n1+h,2)
    alfa[i] = lamda[i]/M

P_min_sr_ABR = [0 for i in range(n1)] #вероятности АБР для минимального среднего
P_min_sr_RBS = [0 for i in range(n1)] #вероятности РБС для минимального среднего
MIN_sr = [0 for i in range(n1)] #минимальные средние

for f in range(n1):
    print('Лямда')
    print(f+1)
    #переменные для эксперементов
    pabs = 0 
    prbs = 0
    minsr = 0
    print('Эксперементы')
    for w in range(n):
        print(w+1)
        Q = np.int32(np.zeros([M+2,S])) #количество сообщений в слоте
        Table = np.int32(np.zeros([n2,n2])) #таблица с вероятностями среднего кол-ва сообщений
        for i in range(n2): # проход по вероятностям АБР
            for j in range(n2): #проход по вероятностям РБС
                mas1 = np.random.poisson(alfa[f],(M,S)) #формирования пришедших сообщений в слот размером 4 на 1000
                Q[:4,0] = mas1[:,0] #первый столбец кол-ва сообщений в слоте
                P = np.int32(np.zeros([M+2,S])) #веротяности передачи АБР и РБС
                for s in range(1,S): #проход по слотам
                    for t in range(M+2): #проход по абоентам и ретронстляторам
                        if t==4 or t==5: #ретронляторы
                            P[t][s] = random.choices([1,0], weights=[p_RBS[j],1-p_RBS[j]])[0] and (Q[t][s-1]>0)
                            Q[4][s] = Q[4][s-1] - (P[4][s]==1 and P[5][s]==0) + (P[0][s]==1 and P[1][s]==0) + (P[1][s]==1 and P[0][s]==0)
                            Q[5][s] = Q[5][s-1] - (P[5][s]==1 and P[4][s]==0) + (P[2][s]==1 and P[3][s]==0) + (P[3][s]==1 and P[2][s]==0)
                        else: #абоненты
                            P[t][s] = random.choices([1,0], weights=[p_ABR[i],1-p_ABR[i]])[0] and (Q[t][s-1]>0)
                            if t%2 == 0:
                                Q[t][s] = mas1[0][s] + Q[t][s-1] - (P[t][s]==1 and P[t+1][s]==0)
                            else:
                                Q[t][s] = mas1[0][s] + Q[t][s-1] - (P[t][s]==1 and P[t-1][s]==0)
                Table[i][j]=sum(np.sum(Q, axis = 0))/S #заполнение таблицы
        r,c = np.unravel_index(Table.argmin(),Table.shape) #нахождение индексов минимального элемента
        pabs += p_ABR[r] #нахождение вероятности АБР
        prbs += p_RBS[c] #нахождение вероятности РБС
        minsr += Table[r][c] #нахождение значения минимального элемента
    #усреднение значений
    P_min_sr_ABR[f] = pabs/n
    P_min_sr_RBS[f] = prbs/n
    MIN_sr[f] = minsr/n
   
fig1 = plt.figure()
ax1 = fig1.add_axes([0,2.4,1,1])
ax1.grid(True, color = [0,0,0])
ax1.set_title('Зависимость оценки среднего количества сообщений в системе от лямды', fontsize = 15)
ax1.plot(lamda, MIN_sr, color='blue')
ax1.set_xlabel('Итенсивность лямда')
ax1.set_ylabel('Среднее число абонентов в буфере')
fig1.savefig('gr1.png', bbox_inches='tight')

fig2 = plt.figure()
ax2 = fig2.add_axes([0,1.2,1,1])
ax2.grid(True, color = [0,0,0])
ax2.set_title('Вероятность отправки сообщения от абонента на ретронслятор', fontsize = 15)
ax2.plot(lamda, P_min_sr_ABR, color='blue')
ax2.set_xlabel('Итенсивность лямда')
ax2.set_ylabel('Вероятсноть pАБР')
fig2.savefig('gr2.png', bbox_inches='tight')

fig3 = plt.figure()
ax3 = fig3.add_axes([0,0,1,1])
ax3.grid(True, color = [0,0,0])
ax3.set_title('Вероятность отправки сообщения от ретронслятор на базовую станцию', fontsize = 15)
ax3.plot(lamda, P_min_sr_RBS, color='blue')
ax3.set_xlabel('Итенсивность лямда')
ax3.set_ylabel('Вероятсноть pРБС')
fig3.savefig('gr3.png', bbox_inches='tight')