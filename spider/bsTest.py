#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author locoder
#  Description :

import urllib2
from bs4 import BeautifulSoup

content = urllib2.urlopen('http://www.baidu.com').read()

scop = BeautifulSoup(content)

print scop.prettify()