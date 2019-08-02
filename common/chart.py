#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author zouziwen
#  Description :

from __future__ import unicode_literals

from pyecharts import Bar
from pyecharts import Pie

bar = Bar("我的第一个图表", "这里是副标题")
bar.add("服装", ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"], [5, 20, 36, 10, 75, 90])
# bar.print_echarts_options() # 该行只为了打印配置项，方便调试时使用
bar.render()    # 生成本地 HTML 文件

class BarRender :

    def __init__(self , title , sub_title):
        self._bar = Bar(title=title , subtitle=sub_title)

    def add(self , title , x , y):
        self._bar.add(title , x , y)

    def render(
        self,
        path="render.html"
    ):
        self._bar.render(path = path)

class PieRender :

    def __init__(self , title , width=1300 , height = 620):
        self._pie = Pie(title , width=width , height = height)

    def add(self, *args, **kwargs):
        self._pie.add(*args, **kwargs)

    def render(self , path="render.html"):
        self._pie.render(path = path)
