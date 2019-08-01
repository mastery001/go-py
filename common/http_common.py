#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author zouziwen
#  Description : http operator

import requests
import socket
import time
import random
import httplib

class HttpOpeator(object):

    def get(self , url , timeout = 2000 , param = None , headers = None):
        while True :
            try :
                rep = requests.get(url , param , headers = headers , timeout = timeout)
                break
            except socket.timeout as e:  # 以下都是异常处理
                print('3:', e)
                time.sleep(random.choice(range(8, 15)))
            except socket.error as e:
                print('4:', e)
                time.sleep(random.choice(range(20, 60)))

        return rep.text

    def post(self , url , timeout = 2000 , param = None , headers = None):
        while True :
            try :
                rep = requests.post(url ,  param , headers = headers , timeout = timeout)
                break
            except socket.timeout as e:  # 以下都是异常处理
                print('3:', e)
                time.sleep(random.choice(range(8, 15)))
            except socket.error as e:
                print('4:', e)
                time.sleep(random.choice(range(20, 60)))

        return rep.text

HttpClient = HttpOpeator()