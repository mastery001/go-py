#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author locoder
#  Description : matplotlib study

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def figure() :
    # 创建空canvas
    fig = plt.figure()
    fig.suptitle('No axes on this figure')

    # 创建2*2的gird
    #fig , ax_lst = plt.subplots(2,2)

    # 调用show方法图像才会显示
    plt.show()

def plot() :
    '''
    只接受np.array or np.ma.masked_array作为输入
    如果参数是pandas data objects 或 np.matrix 则需要转换
    for examples:
    '''
    # a = pd.DataFrame(np.random.rand(4 , 5) , columns = list('abcde'))
    # a_asndarray = a.values
    #
    # plt.plot(a_asndarray)

    # b = np.matrix([[1,2] , [3 ,4]])
    # plt.plot(np.asarray(b))

    x = np.linspace(0, 2, 100)

    plt.plot(x, x, label='linear')
    plt.plot(x, x ** 2, label='quadratic')
    plt.plot(x, x ** 3, label='cubic')

    plt.xlabel('x label')
    plt.ylabel('y label')

    plt.title("Simple Plot")

    plt.legend()

    plt.show()

def figureandplot() :
    fig = plt.figure()
    '''
    等同于 fig.add_subplot(1 , 1 , 1)
    row , column , num
    条件：row * column > num
    将figure定义为row行和column列的网格，num指的是图像的第几行
    '''
    subplot = fig.add_subplot(111)
    x = np.arange(0 , 10 , 0.2)
    y = np.sin(x)

    subplot.plot(x , y)
    plt.show()

if __name__ == '__main__' :
    figureandplot()