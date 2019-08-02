#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author zouziwen
#  Description : db操作

import MySQLdb

class DBConnector :

    def __init__(self , dbname = None):
        self.conn = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='root',
            db=dbname,
            charset = 'utf8'
        )
        self.conn.set_character_set('utf8')
        cursor = self.conn.cursor()
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        self.dbcommit()

    def __del__(self):
        self.conn.close()

    # def dbcursor(self):
    #     return self.conn.cursor()

    def dbcommit(self):
        self.conn.commit()

    def exec_many(self , sql , datas):
        cursor = self.conn.cursor()
        cursor.executemany(sql , datas)
        self.dbcommit()
        return cursor

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