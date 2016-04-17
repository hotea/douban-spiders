# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    publish = scrapy.Field()
    pubdate = scrapy.Field()
    pagenum = scrapy.Field()
    price = scrapy.Field()
    binding = scrapy.Field()
    isbn = scrapy.Field()
    rating_num = scrapy.Field()
    rating_people = scrapy.Field()
    intro = scrapy.Field()



