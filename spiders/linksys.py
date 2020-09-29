import scrapy

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from items import FirmwareImage
from loader import FirmwareLoader

class LinksysSpider(CrawlSpider):
    name = 'linksys'
    allowed_domains = ['linksys.com']
    start_urls = ["http://www.linksys.com/us/support/sitemap/"]
    rules = (
        Rule(LinkExtractor(allow=('sitemap',)), callback='parse_item'),
        Rule(LinkExtractor(allow=('support-product',)), callback='parse_support'),

    )

    def parse_item(self, response):
        self.logger.info(response.url)
        for link in response.xpath("//div[@class='item']//a/@href").extract():
            yield response.follow(link, callback=self.parse_support)

    def parse_support(self, response):
        for link in response.xpath('//div[@id=\'support-downloads\']//a'):
            href = link.xpath("@href").extract()[0]
            text = (link.xpath("text()").extract() or [""])[0]

            if "download" in text.lower():
                product = response.xpath('//span[@class=\'part-number\']/text()').extract()
                yield response.follow(href, meta={'product': product}, callback=self.parse_kb)

    def parse_kb(self, response):
        for entry in reversed(
                response.xpath('//div[@id=\'support-article-downloads\']/div/p')):
            item = FirmwareLoader(
                item=FirmwareImage(),
                response=response
            )
            firmware = []
            release_notes = []
            for url in entry.xpath('//a/@href').extract():
                if 'firmware' in url:
                    firmware.append(url)
                if 'releasenotes' in url:
                    release_notes.append(url)
            item.add_value('releasenotes', release_notes)
            item.add_value('firmware', firmware)
            item.add_value('product', response.meta['product'])
            item.add_value('vendor', self.name)
            yield item.load_item()
