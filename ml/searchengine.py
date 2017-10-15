#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author locoder

import urllib2
import MySQLdb
import re
import sys

from urlparse import urljoin
from bs4 import BeautifulSoup

ignorewords = set(['the' , 'of' , 'to' , 'and' , 'a' , 'in' , 'is' , 'it'])

class dbconnector :

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

class crawler(dbconnector) :


    # 辅助函数，用于获取条目的id，并且如果条目不存在，就将其加入数据库中
    def getentryid(self , table , field , value , createnew=True):
        res = self.querysql("select id from %s where %s='%s'" % (table , field , value))
        if None == res :
            return self.execsql("insert into %s(%s) values ('%s')" % (table , field , value)).lastrowid
        else :
            return res[0]

    # 为每个网页建立索引
    def addtoindex(self , url , soup):
        if self.isindexed(url) : return
        print 'Indexing %s' % url

        # 获取每个单词
        text = self.gettextonly(soup)
        words = self.separatewords(text)

        urlid = self.getentryid('urllist' , 'url' , url)

        for i in range(len(words)) :
            word = words[i]
            if word in ignorewords : continue
            wordid = self.getentryid('wordlist' , 'word' , word)
            self.execsql('insert into wordlocation(urlid , wordid , location) values (%d , %d , %d)' % (urlid , wordid , i))

    # 从一个HTML网页中提取文字(不带标签的)
    def gettextonly(self , soup):
        v = soup.string
        if None == v:
            c = soup.contents
            resulttext = ''
            for t in c :
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else :
            return v.strip()

    # 根据任何非空白字符进行分词处理
    def separatewords(self , text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if '' != s]

    # 如果url已经建立过索引则返回
    def isindexed(self , url):
        u = self.querysql("select id from urllist where url = '%s'" % url)

        if None != u :
            v = self.querysql("select * from wordlocation where urlid = %d" % u[0])
            if None != v : return True
        return False

    # 添加一个关联两个网页的链接
    def addlinkref(self , urlFrom , urlTo , linkText):
        words = self.separatewords(linkText)
        fromid = self.getentryid('urllist' , 'url' , urlFrom)
        toid = self.getentryid('urllist' , 'url' , urlTo)
        if fromid == toid : return
        linkid = self.execsql('insert into link(fromid , toid) values (%d , %d)' % (fromid , toid )).lastrowid
        for word in words :
            if word in ignorewords : continue
            wordid = self.getentryid('wordlist' , 'word' , word)
            self.execsql("insert into linkwords(linkid , wordid) values (%d , %d)" % (linkid , wordid))

    def crawl(self , pages , depth = 2) :
        for i in range(depth) :
            newpages = set()
            for page in pages :
                try :
                    # 设置10秒的超时时间,避免卡死在read方法
                    c = urllib2.urlopen(page , timeout=10)
                except :
                    print "Cound not open %s" % page
                    continue
                try :
                    soup = BeautifulSoup(c.read())
                    self.addtoindex(page , soup)

                    links = soup('a')
                    for link in links :
                        if 'href' in dict(link.attrs) :
                            url = urljoin(page , link['href'])
                            if url.find("'") != -1 : continue
                            url = url.split('#')[0]
                            if url[0:4] == 'http' and not self.isindexed(url) :
                                newpages.add(url)
                            linkText = self.gettextonly(link)
                            self.addlinkref(page , url , linkText)

                    self.dbcommit()
                except Exception , e:
                    print e
                    print 'Could not parse page %s' % page

            pages = newpages

    '''
    PageRank算法：
    根据多次迭代来计算每个url的趋近真实的pr值
    假设有A,B,C,D四个网页，那么PR(A)的计算公式如下：
        PR(A) = 0.15 + 0.85 * (PR(B) / linkcount(B) + PR(C) / linkcount(C) + PR(C) / linkcount(C))
    阻尼因子=0.85，指示用户持续点击每个网页中链接的概率为85%
    '''
    def calculatepagerank(self , iterations = 20):
        # 创建pagerank表，并初始化
        self.execsql(['drop table if exists pagerank'
                    , 'create table pagerank(urlid int primary key , score double )'
                    , 'insert into pagerank select id , 1.0 from urllist'])

        for i in range(iterations) :
            print 'Iteration %d' % i

            for (urlid , ) in self.querysql('select id from urllist' , 1) :
                # pagerank分数的最小值
                # 0.85是阻尼因子
                pr = 0.15

                for (linker ,) in self.querysql('select distinct fromid from link where toid=%d' % urlid , 1) :
                    # 得到链接源对应网页的pagerank值
                    linkingpr = self.querysql('select score from pagerank where urlid = %d' % linker)[0]

                    linkingcount = self.querysql('select count(id) from link where fromid = %d' % linker)[0]

                    pr += 0.85 * (linkingpr / linkingcount)
                self.execsql("update pagerank set score = %f where urlid = %d" % (pr , urlid) , autocommit = False)

        self.dbcommit()
    '''
    数据库表：
        1. urllist : id , url                           url列表
        2. wordlist : id , word                         单词列表
        3. wordlocation : urlid , wordid , location     单词在文档中所处位置的列表
        4. link : id , fromid , toid                    链接关系
        5. linkwords : wordid , linkid                  与链接相关的单词
    '''
    def createindextables(self):
        self.execsql(['create table urllist(id int PRIMARY KEY AUTO_INCREMENT, url varchar(500) not null)'
                     ,'create table wordlist(id int PRIMARY KEY AUTO_INCREMENT, word varchar(500) not null)'
                     ,'create table wordlocation(urlid int, wordid int , location INT ,  KEY `urlid_index` (urlid) , KEY `wordid_index` (wordid))'
                     ,'create table link(id int PRIMARY KEY AUTO_INCREMENT , fromid int , toid int , KEY `fromid_index` (fromid) , KEY `toid_index` (toid))'
                     ,'create table linkwords(wordid int , linkid int , KEY `wordid_index` (wordid))'])

class searcher(dbconnector) :

    SCORE_BY_FREQUENCY = 1
    SCORE_BY_LOCATION = SCORE_BY_FREQUENCY << 2
    SCORE_BY_DISTANCE = SCORE_BY_FREQUENCY << 3
    SCORE_BY_INBOUND = SCORE_BY_FREQUENCY << 4
    SCORE_BY_PAGERANK = SCORE_BY_FREQUENCY << 5

    scorefuns = {SCORE_BY_FREQUENCY : 'frequencyscore'
        , SCORE_BY_LOCATION : 'locationscore'
        , SCORE_BY_DISTANCE : 'distancescore'
        , SCORE_BY_INBOUND : 'inboundlinkscore'
        , SCORE_BY_PAGERANK : 'pagerankscore'}


    '''
    执行sql获取每个url中对应查询单词的位置:
     select w0.urlid , w0.location , ... , wN.location from wordlocation w0 , ... , wordlocation wN where w0*w1*...*wN.urlid and w0.wordid = 'word1' and  ... and wN.wordid = 'wordN'

    返回结果：
        rows：[(url , location1 , .. , locationN)]
        wordids：[word1,...,wordN]
    '''
    def getmatchrows(self , q):
        fieldlist = 'w0.urlid'
        tablelist = ''
        clauselist = ''
        wordids = []

        words = q.split(' ')
        tablenumber = 0

        for word in words :

            wordrow = self.querysql("select id from wordlist where word='%s'" % word)

            if None != wordrow :
                wordid = wordrow[0]
                wordids.append(wordid)
                if tablenumber > 0 :
                    tablelist += ','
                    clauselist += " and w%d.urlid=w%d.urlid and " % (tablenumber - 1 , tablenumber)

                fieldlist += ',w%d.location' % tablenumber
                tablelist += 'wordlocation w%d' % tablenumber
                clauselist += 'w%d.wordid = %d' % (tablenumber , wordid )
                tablenumber += 1

        fullquery = 'select %s from %s where %s' % (fieldlist , tablelist , clauselist)
        #print fullquery

        return [row for row in self.execsql(fullquery)] , wordids


    # 得到查询结果的url的评价值
    def getscoredlist(self , rows , wordids , scorefunctypes = SCORE_BY_FREQUENCY):
        totalscores = dict([(row[0] , 0) for row in rows])

        # if scorefunctypes == self.SCORE_BY_LOCATION :
        #     weights = [(1.0 , self.locationscore(rows))]
        #     # weights = [(1.0 , self.locationscore(rows)) , (1.5 , self.locationscore(rows))]
        # elif scorefunctypes == self.SCORE_BY_DISTANCE :
        #     weights = [(1.0, self.distancescore(rows))]
        #     # weights = [(1.0 , self.distancescore(rows)) , (1.5 , self.distancescore(rows))]
        # else :
        #     weights = [(1.0 , self.frequencyscore(rows))]
        #     #weights = [(1.0 , self.frequencyscore(rows)) , (1.5 , self.frequencyscore(rows))]

        weights = []

        # 多个评价函数可聚合
        if type(scorefunctypes) == int :
            func = self.getscorefunc(scorefunctypes)
            if None == func :
                weights = [(1.0, self.frequencyscore(rows))]
            else :
                weights.append((1.0, func(rows)))
        else :
            for scorefunctype in scorefunctypes :
                func = self.getscorefunc(scorefunctype)
                if None != func:
                    weights.append((1.0, func(rows)))

        for (weight , scores) in weights :
            for url in totalscores :
                totalscores[url] += weight * scores[url]

        return totalscores

    def getscorefunc(self , scorefunctype):
        scorefuncname = self.scorefuns[scorefunctype]
        if hasattr(self, scorefuncname):
            scorefunc = getattr(self, scorefuncname)
            return scorefunc

        return None

    def geturlname(self , id):
        return self.querysql("select url from urllist where id = %d" % id)[0]

    def query(self , q , scorefunctypes = SCORE_BY_FREQUENCY):
        rows , wordids = self.getmatchrows(q)
        scores = self.getscoredlist(rows , wordids , scorefunctypes)
        rankedscores = sorted([(score , url) for url , score in scores.items()] , reverse = 1)
        for score , urlid in rankedscores[:10] :
            print '%f\t%s' % (score , self.geturlname(urlid))

    # 归一化函数
    def normalizescores(self , scores , smallIsBetter = 0):
        vsmall = 0.00001 # 避免被零整除

        # 当值越小时，评价值越高
        if smallIsBetter :
            minscore = min(scores.values())
            return dict([(u , float(minscore) / max(vsmall , l)) for u , l in scores.items()])
        else :
            maxscore = max(scores.values())
            if maxscore == 0 : maxscore = vsmall
            return dict([(u, float(c) / maxscore) for u, c in scores.items()])

    # ******************* 以下为评价函数 ************************ #
    # 根据单词频度来对网页进行打分
    def frequencyscore(self , rows):
        counts = dict([(row[0] , 0) for row in rows])

        for row in rows:
            counts[row[0]] += 1

        return self.normalizescores(counts)

    # 单词位置优先
    def locationscore(self , rows):
        wordlocations = dict([(row[0] , 10000000) for row in rows])

        for row in rows :
            locSum = sum(row[1:])
            if locSum < wordlocations[row[0]] : wordlocations[row[0]] = locSum

        # 参数为1代表值越小评价值越高
        return self.normalizescores(wordlocations , 1)

    # 根据单词间距离来判定
    def distancescore(self , rows):
        if len(rows) <= 2 : return dict([(row[0] , 1.0) for row in rows])

        mindistance = dict([(row[0] , 10000000) for row in rows])

        for row in rows :
            # 单词间距离总和
            distance = sum([abs(row[i] - row[i - 1]) for i in range(2 , len(row))])

            if distance < mindistance[row[0]] :
                mindistance[row[0]] = distance

        return self.normalizescores(mindistance , 1)

    # 利用外部回指链接来评价
    def inboundlinkscore(self , rows):
        uniqueurls = set([row[0] for row in rows])

        inboundlinkcount = dict([(u , self.querysql('select count(*) from link where toid = %d' % u)[0]) for u in uniqueurls])

        return self.normalizescores(inboundlinkcount)

    def pagerankscore(self , rows):
        pageranks = dict([(row[0] , self.querysql('select score from pagerank where urlid = %s' % row[0])[0]) for row in rows])
        # maxrank = max(pageranks.values())
        # normalizedscores = dict([(u , float(l) / maxrank) for (u,l) in pageranks.items()])
        return self.normalizescores(pageranks)


def testsearch(search , q) :

    print 'frequency:\n'
    search.query(q)

    print '\nlocation:\n'
    search.query(q , searcher.SCORE_BY_LOCATION)

    print '\ndistance:\n'
    search.query(q, searcher.SCORE_BY_DISTANCE)

    print '\ninbound:\n'
    search.query(q, searcher.SCORE_BY_INBOUND)

    print '\npagerank:\n'
    search.query(q, searcher.SCORE_BY_PAGERANK)

    print '\nfrequency&distance:\n'
    search.query(q, [searcher.SCORE_BY_FREQUENCY, searcher.SCORE_BY_LOCATION])

    print '\nfrequency&distance:\n'
    search.query(q, [searcher.SCORE_BY_FREQUENCY , searcher.SCORE_BY_DISTANCE])

    print '\nlocation&distance:\n'
    search.query(q, [searcher.SCORE_BY_LOCATION, searcher.SCORE_BY_DISTANCE])

    print '\nfrequency&location&distance&inbound&pagerank:\n'
    search.query(q, [searcher.SCORE_BY_FREQUENCY, searcher.SCORE_BY_LOCATION, searcher.SCORE_BY_DISTANCE , searcher.SCORE_BY_INBOUND, searcher.SCORE_BY_PAGERANK])

    # 基于网页内容和排名
    print '\nlocation&frequency&pagerank:\n'
    search.query(q, [searcher.SCORE_BY_FREQUENCY, searcher.SCORE_BY_LOCATION, searcher.SCORE_BY_PAGERANK])


if __name__ == '__main__':
    crawler = crawler()

    # crawler.createindextables()

    # pagelist = ['http://blog.ziwenzou.com/']
    # crawler.crawl(pagelist)

    #crawler.calculatepagerank()

    testsearch(searcher() , 'git')


