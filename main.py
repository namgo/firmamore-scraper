import scrapy

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class LinksysSpider(CrawlSpider):
    name = 'linksys'
    allowed_domains = ['linksys.com']
    start_urls = ["http://www.linksys.com/us/support/sitemap/"]

    rules = (
        Rule(LinkExtractor( allow=('support-product',)),)
    )

    def parse_item(self, response):
        self.logger.info(response.url)

        link = response.xpath("//div[@class='item']//a/@href").extract()

        return response.follow(link, cb_kwargs=dict(item=item))
