from scrapy.item import Item, Field

class FirmwareImage(Item):
    vendor = Field()
    product = Field(default=None)

    description = Field(default=None)
    version = Field(default=None)
    date = Field(default=None)
    releasenotes = Field()
    firmware = Field()
    files = Field()
    file_urls = Field()
