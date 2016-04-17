# -*- coding: utf-8 -*-

import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
#from scrapy.loader import ItemLoader
#from scrapy import Selector
from bs4 import BeautifulSoup

from douban_subject.items import BookItem


class BookSpider(CrawlSpider):
    name = 'book'
    allowed_domains = ['book.douban.com']
    start_urls = ['https://book.douban.com/']

    rules = (
        Rule(LinkExtractor(allow=r'{}subject/\d+/.*'.format(start_urls[0])), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'{}tag/.*'.format(start_urls[0])), follow=True),
    )

    def parse_item(self, response):
        #l = ItemLoader(item=BookItem(), response=response)
        i = BookItem()
        soup = BeautifulSoup(response.body, 'lxml')
        info = re.sub(r'\n +', '', soup.find('div', id="info").text.strip()) # 书籍信息unicode字符串, u'作者: xxx\n 出版社: xxx\n'
        rating = soup.find('div', class_="rating_self clearfix")
        intro = soup.select('#link-report .intro')
        if len(intro) == 2:
            intro = intro[1].get_text(strip=True)
        else:
            intro = intro[0].get_text(strip=True)
        book = re.split('\n+', str(info.encode('utf-8'))) # 书籍信息字符串数组, ['作者: xxx', '出版社: xxx']
        d = {}
        for k in book:
            kv = k.split(':')
            d.setdefault(kv[0], kv[1].lstrip())
        rating_num = rating.find('strong')
        rating_people = rating.find('span', property="v:votes")

        try:
            i['title'] = soup.find('span', property="v:itemreviewed").text.encode('utf-8')
            i['url'] = response.url.rpartition('/')[0]
            i['author'] = d['作者']
            i['publish'] = d['出版社']
            i['pubdate'] = d['出版年']
            i['pagenum'] = d['页数']
            i['price'] = d['定价']
            i['binding'] = d['装帧']
            i['isbn'] = d['ISBN']
            i['rating_num'] = str(rating_num.text.strip()) if rating_num else 0
            i['rating_people'] = str(rating_people.text) if rating_people else 0
            i['intro'] = str(intro.encode('utf-8'))
        except KeyError:
            pass
        return i
