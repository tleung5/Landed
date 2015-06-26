# # -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http.request import Request
from urlparse import urljoin


NUM_PAGES = 1       # number of pages to scrape    
BASE_URL = 'http://sfbay.craigslist.org/search/pen/apa'

class CraigslistSampleItem(scrapy.Item):
  title = scrapy.Field()
  email = scrapy.Field()
  ID = scrapy.Field()
  url = scrapy.Field()
  description = scrapy.Field()
  phone = scrapy.Field()
  manager = scrapy.Field()


# Crawl San Francisco Bay area Craigslist apartment rental listings
class MySpider(CrawlSpider):
  name = "craigslist"
  allowed_domains = ["craigslist.org"]
  base_url = BASE_URL + "?"
  start_urls = []
  for i in range(0, NUM_PAGES):
    start_urls.append(base_url + "s=" + str(i) + "00" + "&housing_type=2&housing_type=3&housing_type=4&housing_type=5&housing_type=6&housing_type=8&housing_type=9&minAsk=2000&maxAsk=12000")


  # Parse list of posts to extract titles, urls, and Craigslist IDs
  def parse(self, response):
    hxs = response.selector
    titles = hxs.xpath("//span[@class='pl']")
    count = 0
    for titles in titles:
      if count < 2:
        count += 1
        item = CraigslistSampleItem()
        item["title"] = titles.xpath("a/text()").extract()
        url = 'http://sfbay.craigslist.org{}'.format(''.join(titles.xpath("a/@href").extract()))
        item["url"] = url
        item["ID"] = url[36:46]
        yield Request(item['url'], meta = {'item': item}, callback = self.parse_item_page)


  # Parse post to extract description and whether the post is from a property manager
  def parse_item_page(self, response):
    hxs = response.selector
    item = response.request.meta["item"]
    description_list = hxs.xpath('//section[@id="postingbody"]/text()').extract()
    description = ' '.join(description_list)
    item['description'] = description

    exp = re.compile("(?i)Management|Realty|Apartment|Broker|Agent|Real Estate")
    manager = exp.search(description)
    if manager is None:
        item["manager"] = "FALSE"
    else:
        item["manager"] = "TRUE"

    reply_url = (BASE_URL + '/{}').format(''.join(item['ID']))
    yield Request(reply_url, meta = {'item': item}, callback = self.parse_reply_page)


  # Parse reply page to extract email and phone number
  def parse_reply_page(self, response):
    hxs = response.selector
    item = response.request.meta["item"]
    item["email"] = hxs.xpath('.//div[@class="anonemail"]/text()').extract()
    reply_list = hxs.xpath('.//div[@class="reply_options"]').extract()
    reply = ''.join(reply_list)
    phone_exp = re.search("contact by phone:", reply)
    if phone_exp:
        number_exp = re.search("\d", reply[match.end():])
        index = phone_exp.end() + number_exp.start()
        phone = reply[index:index + 15]
        phone = re.sub('[()\-<\/li>]', '', phone)
        print(phone)
        item["phone"] = phone
    else:
        item["phone"] = "None"

    yield item


    