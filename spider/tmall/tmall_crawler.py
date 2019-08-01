#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author zouziwen
#  Description :

from common.http_common import HttpClient
import random
from bs4 import BeautifulSoup
import json

# 销量从高到低排名
TMALL_PRODUCT_URL = "https://list.tmall.com/search_product.htm?q={query}&sort=d"

header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'user-agent': "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    'cache-control': 'max-age=0'
}  # request 的请求头

class TmallCrawler:

    def crawl(self , query):
        url = TMALL_PRODUCT_URL.format(query = query)
        content = HttpClient.get(url , timeout=random.choice(range(200 , 400)) , headers=header)
        soup = BeautifulSoup(content , "lxml")
        print soup.prettify()


    def getComment(self):
        newHeader = header.copy()
        newHeader['Referer'] = 'https://detail.tmall.com/item.htm?spm=1&id=1&skuId=1&user_id=1&cat_id=2&is_b=1&rn=1'
        url = "https://rate.tmall.com/list_detail_rate.htm?itemId=555962105657&spuId=864172717&sellerId=3302702400&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&ua=098%23E1hvg9vBvLIvUvCkvvvvvjiPRFFO6jY8Psdy0j3mPmPUQji8PscWzjYRPszZ1jtndphvmpvUEvbAG92WR46CvvyvmbWmeE9vdWorvpvBUvkT9NbAvhLK84GuUZWE3weCvpvJjFsr7qjNznswSnY4wgRIkveCS%2BPkRG5U9ZFVAcW23QhvCvvhvvvPvpvhvv2MMQhCvvOvUvvvphmEvpvVmvvC9camuphvmvvv92OWVW%2BRKphv8vvvvUrvpvvvvvmmZhCvCbQvvUEpphvWh9vv9DCvpvsOvvmmZhCv2n9EvpCW2nSevvwDkbmxfXuKNZAQiNLUeCr1caeYiXhpVj%2BO3w0x9CQaWDNBlwethbUf8cc6D70XdeQHYExrA8TNa6j9sRFyViD07reYiXhpV2yCvvpvvvvviQhvCvvv9U8rvpvEvvsB9jrqvCklRphvCvvvvvmCvpvWzCAOc%2BzNznswOKn4RphvCvvvvvv%3D&needFold=0&_ksTS=1564644550780_1474&callback=jsonp1475"
        content = HttpClient.get(url, timeout=random.choice(range(200, 400)), headers=newHeader)
        start = content.index('(')
        content = content[start+1:-1]
        # print content

        return json.loads(content)

    # 获取商品评论最大页数
    def getLastPage(self, itemId):
        tmalljson = self.getComment()
        return tmalljson['rateDetail']['paginator']['lastPage']  # 最大页数



if __name__ == '__main__':
    t = TmallCrawler()
    t.crawl("皮衣")
    # print t.getComment()
    # print t.getLastPage(1)