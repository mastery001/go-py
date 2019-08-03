#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author zouziwen
#  Description :

class FileWrite:

    def __init__(self , fileName , read=False):
        mode = 'w'
        if read :
            mode = 'rw'
        self._f = open(fileName , mode)

    def __del__(self):
        self._f = None

    def write(self , line):
        self._f.writelines('%s \r\n' % line)

    def read(self):
        return self._f


    def flush_and_close(self):
        self._f.flush()
        self._f.close()

