#  -*- coding: utf-8 -*-
# ! /usr/bin/env python
#  Author zouziwen
#  Description :

from common.http_common import HttpClient
from common.dbconnector import DBConnector
import random
from bs4 import BeautifulSoup
import json

# 销量从高到低排名
TMALL_PRODUCT_URL = "https://list.tmall.com/search_product.htm?q={query}&sort=d"

# url = "https://rate.tmall.com/list_detail_rate.htm?itemId=555962105657&spuId=864172717&sellerId=3302702400&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&ua=098%23E1hvg9vBvLIvUvCkvvvvvjiPRFFO6jY8Psdy0j3mPmPUQji8PscWzjYRPszZ1jtndphvmpvUEvbAG92WR46CvvyvmbWmeE9vdWorvpvBUvkT9NbAvhLK84GuUZWE3weCvpvJjFsr7qjNznswSnY4wgRIkveCS%2BPkRG5U9ZFVAcW23QhvCvvhvvvPvpvhvv2MMQhCvvOvUvvvphmEvpvVmvvC9camuphvmvvv92OWVW%2BRKphv8vvvvUrvpvvvvvmmZhCvCbQvvUEpphvWh9vv9DCvpvsOvvmmZhCv2n9EvpCW2nSevvwDkbmxfXuKNZAQiNLUeCr1caeYiXhpVj%2BO3w0x9CQaWDNBlwethbUf8cc6D70XdeQHYExrA8TNa6j9sRFyViD07reYiXhpV2yCvvpvvvvviQhvCvvv9U8rvpvEvvsB9jrqvCklRphvCvvvvvmCvpvWzCAOc%2BzNznswOKn4RphvCvvvvvv%3D&needFold=0&_ksTS=1564644550780_1474&callback=jsonp1475"
TMALL_COMMENT_URL = "https://rate.tmall.com/list_detail_rate.htm?itemId={itemId}&sellerId=1&order=3&currentPage={currentPage}&content=1&callback=jsonp1475"

COMMENT_SQL = "insert into product_comment(word_category , search_word , date , content , sku , source) values(%s , %s , %s , %s , %s , %s)"

header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'user-agent': "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    'cache-control': 'max-age=0'
}  # request 的请求头


class Comment(object):
    def __init__(self, date='', content='', sku='', source='', search_word='', word_category=''):
        self._date = date
        self._content = content
        self._sku = sku
        self._source = source
        self._search_word = search_word
        self._word_category = word_category
        self._i = 0

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = date

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

    @property
    def sku(self):
        return self._sku

    @sku.setter
    def sku(self, sku):
        self._sku = sku

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

    @property
    def search_word(self):
        return self._search_word

    @search_word.setter
    def search_word(self, search_word):
        self._search_word = search_word

    @property
    def word_category(self):
        return self._word_category

    @search_word.setter
    def word_category(self, word_category):
        self._word_category = word_category

    def __iter__(self):
        return self

    def next(self):
        if self._i == 0:
            self._i += 1
            return self._word_category
        elif self._i == 1:
            self._i += 1
            return self._search_word
        elif self._i == 2:
            self._i += 1
            return self._date
        elif self._i == 3:
            self._i += 1
            return self._content
        elif self._i == 4:
            self._i += 1
            return self._sku
        elif self._i == 5:
            self._i += 1
            return self._source
        else:
            raise StopIteration()


class TmallCrawler:
    def __init__(self):
        self.conn = DBConnector('tmall')

    def crawl(self, query):
        productIds = self.getProductId(query=query)
        # total = len(productIds)
        # i = 0
        # while i < total :
        commentList = []
        for id in productIds:
            maxPage = self.getLastPage(id)
            for page in range(1, maxPage + 1):
                commentJson = self.getComment(id, page)

                # 评论列表
                rateList = commentJson['rateDetail']['rateList']

                n = len(rateList)

                i = 0

                while i < n:
                    commentBean = Comment(date=rateList[i]['rateDate'], content=rateList[i]['rateContent'],
                                          sku=rateList[i]['auctionSku'], source=rateList[i]['cmsSource'],
                                          search_word=query)
                    commentList.append(commentBean)
                    i += 1

            break

        return commentList

    # 获取query词下的所有商品id
    def getProductId(self, query):
        url = TMALL_PRODUCT_URL.format(query=query)
        print url
        content = HttpClient.get(url, timeout=random.choice(range(200, 400)), headers=header)
        soup = BeautifulSoup(content, "lxml")
        product_list = soup.find_all('div', {'class': 'product'})
        idList = []
        for product in product_list:
            idList.append(product['data-id'])
        # print soup.prettify()
        return idList

    # 获取商品评论
    def getComment(self, itemId, currentPage):
        newHeader = header.copy()
        newHeader['Referer'] = 'https://detail.tmall.com/item.htm?spm=1&id=1&skuId=1&user_id=1&cat_id=2&is_b=1&rn=1'
        url = TMALL_COMMENT_URL.format(itemId=itemId, currentPage=currentPage)
        content = HttpClient.get(url, timeout=random.choice(range(200, 400)), headers=newHeader)
        start = content.index('(')
        content = content[start + 1:-1]
        # print content

        return json.loads(content)

    # 获取商品评论最大页数
    def getLastPage(self, itemId):
        tmalljson = self.getComment(itemId, 1)
        return tmalljson['rateDetail']['paginator']['lastPage']  # 最大页数

    def persist(self, word_category, commentList):
        maxInsert = 50

        datas = []
        i = 0

        for comment in commentList:
            i += 1
            if i % maxInsert == 0:
                self.conn.exec_many(COMMENT_SQL, datas)
                datas = []
                continue

            comment._word_category = word_category
            datas.append(comment)

        if i % maxInsert != 0:
            self.conn.exec_many(COMMENT_SQL, datas)


if __name__ == '__main__':
    t = TmallCrawler()
    commentList = t.crawl("皮衣")
    t.persist('皮衣', commentList)
    # print t.getComment(555962105657 , 1)
    # print t.getLastPage(1)
