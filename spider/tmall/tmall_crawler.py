#  -*- coding: utf-8 -*-
# ! /usr/bin/env python
#  Author zouziwen
#  Description :

from common.http_common import HttpClient
from common.dbconnector import DBConnector
from common.fileutil import FileWrite
import random
import bs4
from bs4 import BeautifulSoup
import json
import ast


# 销量从高到低排名
TMALL_PRODUCT_URL = "https://list.tmall.com/search_product.htm?q={query}&sort=d"

# url = "https://rate.tmall.com/list_detail_rate.htm?itemId=555962105657&spuId=864172717&sellerId=3302702400&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&ua=098%23E1hvg9vBvLIvUvCkvvvvvjiPRFFO6jY8Psdy0j3mPmPUQji8PscWzjYRPszZ1jtndphvmpvUEvbAG92WR46CvvyvmbWmeE9vdWorvpvBUvkT9NbAvhLK84GuUZWE3weCvpvJjFsr7qjNznswSnY4wgRIkveCS%2BPkRG5U9ZFVAcW23QhvCvvhvvvPvpvhvv2MMQhCvvOvUvvvphmEvpvVmvvC9camuphvmvvv92OWVW%2BRKphv8vvvvUrvpvvvvvmmZhCvCbQvvUEpphvWh9vv9DCvpvsOvvmmZhCv2n9EvpCW2nSevvwDkbmxfXuKNZAQiNLUeCr1caeYiXhpVj%2BO3w0x9CQaWDNBlwethbUf8cc6D70XdeQHYExrA8TNa6j9sRFyViD07reYiXhpV2yCvvpvvvvviQhvCvvv9U8rvpvEvvsB9jrqvCklRphvCvvvvvmCvpvWzCAOc%2BzNznswOKn4RphvCvvvvvv%3D&needFold=0&_ksTS=1564644550780_1474&callback=jsonp1475"
TMALL_COMMENT_URL = "https://rate.tmall.com/list_detail_rate.htm?itemId={itemId}&sellerId=1&order=3&currentPage={currentPage}&content=1&callback=jsonp1475"

COMMENT_SQL = "insert into product_comment(word_category , search_word , date , content , sku , source) values(%s , %s , %s , %s , %s , %s)"
PRODUCT_COMMENT_SQL = "insert into product_info_comment(product_id , price , title , shop , month_buy_total , comment_count  , date , content , sku , source , search_word , word_category) values(%s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s)"

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

class TmallLocalPersist :

    def __init__(self , query , read = False):
        self._fileWrite = FileWrite('tmall_%s.txt' % query)

    def __del__(self):
        self._fileWrite = None

    def write(self , id , page , json):
        self._fileWrite.write("%s$%s$%s" % (id , page , json))

    def read(self):
        comments = {}
        for line in self._fileWrite.read() :
            row = line.split('$')
            if row[0] not in comments :
                comments[row[0]] = []
            comments[row[0]].append(ast.literal_eval(row[2]))
        return comments

    def close(self):
        self._fileWrite.flush_and_close()

class TmallCrawler:
    def __init__(self):
        self.conn = DBConnector('tmall')

    def crawl(self, query):
        product_infos = self.getProductInfo(query = query)

        datas = []

        localPersist = TmallLocalPersist(query)

        for product in product_infos :
            id = product['id']
            commentJson, maxPage = self.getLastPage(id)

            for page in range(1, maxPage + 1):
                try:
                    # commentJson = self.getComment(id, page)
                    if page > 1 :
                        commentJson = self.getComment(id, page)

                    localPersist.write(id, page, commentJson)

                    # 评论列表
                    rateList = commentJson['rateDetail']['rateList']


                    n = len(rateList)

                    i = 0

                    while i < n:
                        data = product.copy()

                        data['date'] = rateList[i]['rateDate']
                        data['content'] = rateList[i]['rateContent']
                        data['sku'] = rateList[i]['auctionSku']
                        data['source'] = rateList[i]['cmsSource']
                        data['search_word'] = query

                        datas.append(data)

                        i += 1
                        # break
                except Exception as e:
                    print(e)

            # break

        localPersist.close()

        return datas


    def crawlComment(self, query):
        productIds = self.getProductId(query=query)


        commentList = []

        localPersist = TmallLocalPersist(query)

        for id in productIds:
            commentJson , maxPage = self.getLastPage(id)

            for page in range(1, maxPage + 1):
                try:
                    # commentJson = self.getComment(id, page)
                    if page > 1 :
                        commentJson = self.getComment(id, page)

                    localPersist.write(id, page, commentJson)

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
                except Exception as e:
                    print(e)
            # break

        localPersist.close()

        return commentList

    def getProductInfo(self , query , save=False):
        url = TMALL_PRODUCT_URL.format(query=query)
        # print url
        content = HttpClient.get(url, timeout=random.choice(range(200, 400)), headers=header)
        soup = BeautifulSoup(content, "lxml")
        product_list = soup.find_all('div', {'class': 'product'})

        # price_list = soup.find_all('p' , {'class' : 'productPrice'})
        # price_list[0].contents[3]['title']

        # shop_list = soup.select('.productShop')

        product_infos = []

        for product in product_list:

            product_info = {}

            product_info['id'] = product['data-id']

            ## 从class="product-iWrap" div下获取
            for child in product.contents[1].children:
                try :
                    if type(child) == bs4.element.NavigableString :
                        continue

                    clz = child['class'][0]

                    if clz == 'productPrice' :

                        product_info['price'] = self.findElement(child , 'em')[0]['title']

                    if clz == 'productTitle' :
                        product_info['title'] = self.findElement(child, 'a')[0].string.encode('utf8').strip()


                    if clz == 'productShop' :
                        product_info['shop'] = self.findElement(child, 'a')[0].string.encode('utf8').strip()


                    if clz == 'productStatus' :
                        elements = self.findElement(child, 'span')
                        product_info['month_buy_total'] = self.findElement(elements[0], 'em')[0].string.encode('utf8').strip()

                        product_info['month_buy_total'] = product_info['month_buy_total'].split('笔')[0]

                        product_info['comment_count'] = self.findElement(elements[1], 'a')[0].string.encode('utf8').strip()

                except Exception as e :
                    # print e
                    continue

            product_infos.append(product_info)

        if save :
            file_write = FileWrite('tmall_商品_%s.txt' % query)
            for p in product_infos :
                file_write.write(p)

            file_write.flush_and_close()

        return product_infos

    def findElement(self , element , name):
        elements = []
        for c in element.contents:
            if type(c) == bs4.element.Tag and c.name == name:
                elements.append(c)

        return elements

    # 获取query词下的所有商品id
    def getProductId(self, query):
        url = TMALL_PRODUCT_URL.format(query=query)
        # print url
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

        print("start get item %s page %d " % (itemId , currentPage))

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
        return tmalljson , tmalljson['rateDetail']['paginator']['lastPage']  # 最大页数

    def persist(self, word_category, datas):
        maxInsert = 200

        rows = []
        i = 0

        for data in datas:
            i += 1
            if i % maxInsert == 0:
                self.conn.exec_many(PRODUCT_COMMENT_SQL, rows)
                print("插入成功%d条" % i)
                rows = []
                continue
            try :
                row = [
                    data['id'],
                    data['price'],
                    data['title'] if 'title' in data else 'unknown',
                    data['shop'] if 'shop' in data else 'unknown',
                    data['month_buy_total'].split('笔')[0] if 'month_buy_total' in data else '0',
                    data['comment_count'] if 'comment_count' in data else '0',
                    data['date'],
                    data['content'],
                    data['sku'],
                    data['source'],
                    data['search_word'],
                    word_category
                ]
            except Exception as e :
                print data
                raise e

            rows.append(row)

        if i % maxInsert != 0:
            self.conn.exec_many(PRODUCT_COMMENT_SQL, rows)
            print("插入成功%d条" % i)

    def persistComment(self, word_category, commentList):
        maxInsert = 50

        datas = []
        i = 0

        for comment in commentList:
            i += 1
            if i % maxInsert == 0:
                self.conn.exec_many(COMMENT_SQL, datas)
                print("插入成功%d条" % i)
                datas = []
                continue

            comment._word_category = word_category
            datas.append(comment)

        if i % maxInsert != 0:
            self.conn.exec_many(COMMENT_SQL, datas)
            print("插入成功%d条" % i)

    def getAll(self , column , condition , value):
        return self.conn.querysql("select %s from product_info_comment where %s = '%s'" % (column , condition , value) , 1)


    # def getOne(self , column):
    #     return self.conn.querysql("""
    #         select %s from product_info_comment
    #     """ % column)

    def readProductInfo(self , query):
        file_write = FileWrite('tmall_商品_%s.txt' % query)

        product_infos = []

        for line in file_write.read():
            product_infos.append(ast.literal_eval(line))

        return product_infos

    def readCommentInfo(self , query):
        local = TmallLocalPersist(query , read=True)
        datas = local.read()
        local.close()
        return datas

    def readLocalFile(self , query):
        product_infos = self.readProductInfo(query)

        comments = self.readCommentInfo(query)

        datas = []

        for product in product_infos :
            if product['id'] in comments :
                for commentJson in comments[product['id']] :
                    try:

                        # 评论列表
                        rateList = commentJson['rateDetail']['rateList']

                        n = len(rateList)

                        i = 0

                        while i < n:
                            data = product.copy()

                            data['date'] = rateList[i]['rateDate']
                            data['content'] = rateList[i]['rateContent']
                            data['sku'] = rateList[i]['auctionSku']
                            data['source'] = rateList[i]['cmsSource']
                            data['search_word'] = query

                            datas.append(data)

                            i += 1
                            # break
                    except Exception as e:
                        print(e)

        return datas

# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
# print(sys.getdefaultencoding())

# json = json.loads("{\"rateDetail\":{\"rateCount\":{\"total\":1,\"shop\":0,\"picNum\":1,\"used\":0},\"rateDanceInfo\":{\"storeType\":4,\"currentMilles\":1564711298347,\"showChooseTopic\":false,\"intervalMilles\":295438347},\"rateList\":[{\"auctionPicUrl\":\"\",\"userInfo\":\"\",\"displayRatePic\":\"\",\"dsr\":0,\"displayRateSum\":0,\"appendComment\":null,\"fromMemory\":0,\"picsSmall\":[],\"tmallSweetPic\":\"\",\"rateDate\":\"2019-07-29 23:57:40\",\"rateContent\":\"为啥都没人评论勒？？？？\",\"fromMall\":true,\"userIdEncryption\":\"\",\"sellerId\":672733129,\"displayUserLink\":\"\",\"id\":1053378826253,\"aliMallSeller\":false,\"reply\":\"\",\"pics\":[\"//img.alicdn.com/bao/uploaded/i3/O1CN01zl05w41Z02d9yBfzD_!!0-rate.jpg\"],\"buyCount\":0,\"userVipLevel\":0,\"auctionSku\":\"颜色分类:黑色;尺码:36/S/160\",\"anony\":true,\"displayUserNumId\":0,\"goldUser\":false,\"attributesMap\":null,\"tradeEndTime\":{\"date\":29,\"hours\":23,\"seconds\":58,\"month\":6,\"timezoneOffset\":-480,\"year\":119,\"minutes\":56,\"time\":1564415818000,\"day\":1},\"headExtraPic\":\"\",\"aucNumId\":0,\"displayUserNick\":\"l***0\",\"structuredRateList\":[],\"carServiceLocation\":\"\",\"userVipPic\":\"\",\"serviceRateContent\":\"\",\"memberIcon\":\"\",\"attributes\":\"\",\"position\":\"\",\"cmsSource\":\"天猫\",\"tamllSweetLevel\":0,\"gmtCreateTime\":{\"date\":29,\"hours\":23,\"seconds\":40,\"month\":6,\"timezoneOffset\":-480,\"year\":119,\"minutes\":57,\"time\":1564415860000,\"day\":1},\"useful\":true,\"displayUserRateLink\":\"\"}],\"searchinfo\":\"\",\"from\":\"search\",\"paginator\":{\"lastPage\":1,\"page\":1,\"items\":1},\"tags\":[]}}")

if __name__ == '__main__':
    t = TmallCrawler()

    # category = '皮裙'
    # query = '真皮 皮裙 女'

    # category = '皮衣'
    # query = '真皮 皮衣 女'

    category = '皮衣'
    query = '真皮 皮衣 中长款 女'

    # t.getProductInfo('真皮 皮裙 女' , save=True)

    # t.readProductInfo('真皮 皮裙 女')
    # t.readCommentInfo('真皮 皮裙 女')

    # datas = t.readLocalFile(query)

    # t.persist(category , datas)


    # datas = t.crawl(query)

    # t.persist('皮衣', datas)

    # commentList = t.crawl("皮衣 女")

    # query = "皮衣"
    #
    # commentList = []
    #
    # # 评论列表
    # rateList = json['rateDetail']['rateList']
    #
    # n = len(rateList)
    #
    # i = 0
    #
    # while i < n:
    #     commentBean = Comment(date=rateList[i]['rateDate'], content=rateList[i]['rateContent'],
    #                           sku=rateList[i]['auctionSku'], source=rateList[i]['cmsSource'],
    #                           search_word=query)
    #     commentList.append(commentBean)
    #     i += 1

    # t.persist('皮衣', commentList)
    # print t.getComment(555962105657 , 1)
    # print t.getLastPage(1)
