import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CnbilItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CnbilSpider(scrapy.Spider):
	name = 'cnbil'
	start_urls = ['https://www.cnbil.com/Newsroom/cnb-news/']

	def parse(self, response):
		articles = response.xpath('//article[@class="news-post"]')
		for article in articles:
			out_content = article.xpath('.//span[contains(@id,"content_ctl00_lvNews_lblBlurb_")]//text()').get().strip()
			post_links = article.xpath('.//h2/a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(out_content= out_content))

	def parse_post(self, response, out_content):
		date = response.xpath('//span[@id="content_ctl00_lblDatePosted"]/text()').get()
		title = response.xpath('//h1/span/text()').get()
		content = response.xpath('//div[@class="news-detail-copy"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CnbilItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		if not content:
			item.add_value('content', out_content)
		item.add_value('date', date)

		yield item.load_item()
