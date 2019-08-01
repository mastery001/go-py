#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author zouziwen
#  Description : db操作

import MySQLdb

class DBConnector :

    def __init__(self , dbname = 'searcher'):
        self.conn = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='root',
            db=dbname,
        )

    def __del__(self):
        self.conn.close()

    # def dbcursor(self):
    #     return self.conn.cursor()

    def dbcommit(self):
        self.conn.commit()

    def execsql(self , sqls , autocommit = True):
        cursor = self.conn.cursor()
        if type(sqls) == str or type(sqls) == unicode:
            cursor.execute(sqls)
        else :
            for sql in sqls :
                cursor.execute(sql)
        if autocommit :
            self.dbcommit()
        return cursor

    def querysql(self , sql , oper = 0):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        if oper != 0 :
            return cursor.fetchall()
        return cursor.fetchone()