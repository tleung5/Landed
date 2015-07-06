# # -*- coding: utf-8 -*-
# File: craigslist.py
# Author: Thomas Leung
# Scrapes Craigslist rental listings and extracts data to a .csv file.


import scrapy
import re
import random
import time
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http.request import Request
from urlparse import urljoin


NUM_PAGES = 1                 # number of pages (100 posts per page) to scrape
CITY = 'sfbay'                # city to search
AREA = 'pen'                  # area to search
FILTERS = "&housing_type=2&housing_type=3&housing_type=4&housing_type=5&housing_type=6&housing_type=8&housing_type=9&minAsk=2000&maxAsk=12000"      # search filters
DELAY = 30                    # seconds between each request


# Stores data extracted from posts
class CraigslistItem(scrapy.Item):
  title = scrapy.Field()          # title of post
  url = scrapy.Field()            # url for post
  ID = scrapy.Field()             # Craigslist ID of post
  description = scrapy.Field()    # text of post
  email = scrapy.Field()          # contact email address
  phone = scrapy.Field()          # contact phone number
  manager = scrapy.Field()        # TRUE if property manager, FALSE if not property manager


# Crawl and scrape Craigslist rental listings to extract data from each post
# to a .csv file.  From each post, we extract the title, url,
# Craigslist ID, description, contact email address, and contact phone number.
class MySpider(CrawlSpider):
  name = "craigslist"
  allowed_domains = ["craigslist.org"]
  base_url = "http://" + CITY + ".craigslist.org/search/" + AREA + "/apa?"
  start_urls = []
  for i in range(0, NUM_PAGES):
    start_urls.append(base_url + "s=" + str(i) + "00" + FILTERS)


  # Parse list of posts to extract titles, urls, and Craigslist IDs
  def parse(self, response):
    hxs = response.selector
    titles = hxs.xpath("//span[@class='pl']")

    count = 0
    for titles in titles:
      if count < 1:
        count += 1
        item = CraigslistItem()
        item["title"] = titles.xpath("a/text()").extract()
        url = ("http://" + CITY + ".craigslist.org{}").format(''.join(titles.xpath("a/@href").extract()))
        item["url"] = url
        item["ID"] = url[36:46]
        time.sleep(random.randrange(0, DELAY))
        yield Request(item["url"], meta = {"item": item}, callback = self.parse_item_page)


  # Parse post to extract description and whether the post is from a property manager
  def parse_item_page(self, response):
    hxs = response.selector
    item = response.request.meta["item"]
    description_list = hxs.xpath('//section[@id="postingbody"]/text()').extract()
    description = ' '.join(description_list)
    item["description"] = description

    exp = re.compile("(?i)Management|Realty|Apartment|Broker|Agent|Real Estate")
    manager = exp.search(description)
    if manager is None:
      item["manager"] = "FALSE"
    else:
      item["manager"] = "TRUE"

    reply_url = ("http://" + CITY + ".craigslist.org/reply/" + AREA + "/apa/{}").format(''.join(item["ID"]))
    time.sleep(random.randrange(0, DELAY))
    yield Request(reply_url, meta = {"item": item}, callback = self.parse_reply_page)


  # Parse reply page to extract email address and phone number for each post
  def parse_reply_page(self, response):
    hxs = response.selector
    item = response.request.meta["item"]
    item["email"] = hxs.xpath('.//div[@class="anonemail"]/text()').extract()
    reply_list = hxs.xpath('.//div[@class="reply_options"]').extract()
    reply = ''.join(reply_list)
    phone_exp = re.search("contact by phone:", reply)
    if phone_exp:
      number_exp = re.search("\d", reply[phone_exp.end():])
      index = phone_exp.end() + number_exp.start()
      phone = reply[index:index + 15]
      phone = re.sub("[()\-<\/li>]", "", phone)
      item["phone"] = phone
    else:
        item["phone"] = "FALSE"
    time.sleep(random.randrange(0, DELAY))
    yield item


    