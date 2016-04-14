# coding: utf-8

from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from scrapy_douban.items import DoubanLink
import re


class DoubanSpider(Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['http://www.douban.com/']


    def parse(self, response):
        sel = Selector(response)
        links = sel.xpath('//a[@href]')
        
        for link in links:
            item = DoubanLink()
            url = str(link.re(r'href="(.*?)"')[0])
            if url:
                if not url.startswith('http'):
                    url = response.url + url
                yield Request(url, callback=self.parse)
                item['link'] = url

                url_text = link.xpath('text()').extract()
                if url_text:
                    item['link_text'] = str(url_text[0].encode('utf-8').strip())
                else:
                    item['link_text'] = None
               # print item['link'],
               # print item['link_text']
                yield item



