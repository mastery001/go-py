#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author zouziwen
#  Description :

from spider.tmall.tmall_crawler import TmallCrawler
from common.chart import PieRender

import sys
reload(sys)
sys.setdefaultencoding('utf8')

tmall = TmallCrawler()

colorset = ['黑' , '黄' , '红' , '棕' , '绿' , '白' , '米' , '灰' , '卡其' , '蓝' , '粉' , '紫']

sizeset = ['XXXL' , '3XL' , 'XXL' , '2XL' , 'XL' , 'L' , 'M' , 'S']

def findColor(full , color) :
    # color = color.decode('utf8')
    for c in colorset :
        if c in color:
            return c

    # print full , color

    return "unknown"

def showColor(category) :
    rows = tmall.getAll('sku', 'word_category' , category)
    colors = {}
    for row in rows :
        color = row[0]
        # color = row[0].split(';')[0].split(':')[1]

        color = findColor(row[0] , color)

        if color not in colors :
            colors[color] = 0
        colors[color] += 1

    return colors

def findSize(full , size) :
    # color = color.decode('utf8')
    for s in sizeset:
        if s in size:
            if s == '2XL' :
                s = 'XXL'
            if s == '3XL' :
                s = 'XXXL'
            return s

    print full , size

    return "unknown"

def showSize(category) :
    rows = tmall.getAll('sku' , 'word_category' , category)
    sizes = {}
    for row in rows:
        size = row[0]
        # size = row[0].split(';')[1].split(':')[1]

        size = findSize(row[0], size)

        if size not in sizes:
            sizes[size] = 0
        sizes[size] += 1

    return sizes

def render(name , title , map , path):
    pieRender = PieRender(name)

    pieRender.add(title, map.keys(), map.values(), is_label_show=True)

    pieRender.render(path)

if __name__ == '__main__':

    # colors = showColor('皮衣')
    # sizes = showSize('皮衣')
    #
    # render('女皮衣' , "颜色" , colors , 'piyi_color.html')
    # render('女皮衣' , "尺码" , sizes , 'piyi_size.html')

    colors = showColor('皮裙')
    sizes = showSize('皮裙')

    render('女皮裙' , "颜色" , colors , 'piqun_color.html')
    render('女皮裙' , "尺码" , sizes , 'piqun_size.html')


    # pie = Pie('' , width=1300 , height = 620)

    # for k , v in colors.iteritems() :
    #     print("%s=%d" % (k , v))
