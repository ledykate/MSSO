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
S = 100#1000  # количество слотов в целом
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

#P_min_sr_ABR = [0 for i in range(n1)]  # вероятности АБР для минимального среднего
#P_min_sr_RBS = [0 for i in range(n1)]  # вероятности РБС для минимального среднего
#MIN_sr = [0 for i in range(n1)]  # минимальные средние
    
buf_ret_start = np.int32(np.zeros([N,S])) # Хранит значения сообщений на начало слота для каждого Ретранслятора
buf_ret_end = np.int32(np.zeros([N,S])) # Хранит значения сообщений на конец слота для каждого Ретранслятора
tr_message_ABR = np.int32(np.zeros([M,S])) # Потенциально передаваемые сообщения от АБ (если не будет конфликта)
message_ABtoR = np.int32(np.zeros([N,S])) # Реально переданые сообщения
tr_message_RBS = np.int32(np.zeros([N,S])) # Потенциально передаваемые сообщения от ретранслятора (если не будет конфликта)
buf_ab_start = np.int32(np.zeros([M,S])) # Хранит значения сообщений на начало слота для каждого из АБ
buf_ab_end = np.int32(np.zeros([M,S])) # Хранит значения сообщений на конец слота для каждого из АБ
Table = np.int32(np.zeros([n2, n2]))
MIN_sr = np.int32(np.zeros([1, n1]));

