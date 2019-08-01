#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author locoder
#  Description :  重复统计

def readData(filename) :
    datas = []
    f = open(filename, 'r')
    a = ''
    line = f.readline()
    while line:
        datas.append(line.strip())
        line = f.readline()
    f.close()
    return datas

def dupCount(datas) :
    dupCountDict = {}
    for data in datas :
        if data in dupCountDict :
            dupCountDict[data] += 1
        else :
            dupCountDict[data] = 1

    return dupCountDict

if __name__ == '__main__':
    datas = readData('dupCounterFile')

    dupCountDict = dupCount(datas)

    count = 0
    for i in dupCountDict :
        print i + ',' + str(dupCountDict[i])
        # value = int(dupCountDict[i])
        # if value < 4 :
        #     count+=1

    # print count