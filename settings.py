BOT_NAME = "firmware"

SPIDER_MODULES = ["spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

ITEM_PIPELINES = {
    "pipelines.FirmwarePipeline": 1,
}


AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0
AUTOTHROTTLE_MAX_DELAY = 15
CONCURRENT_REQUESTS = 16


DOWNLOAD_TIMEOUT = 1200
DOWNLOAD_MAXSIZE = 0
DOWNLOAD_WARNSIZE = 0

ROBOTSTXT_OBEY = False
USER_AGENT = "FirmamoreBot/1.0 (+https://github.com/firmadyne/scraper)"

# 
# AWS_SECRET_ACCESS_KEY = 'AplkIjO50tst7R8HGc362W2BEBEqXiBLN7UedCzaROQ'
FILES_STORE = './output/'

FEEDS = {
    'items.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': None,
        'indent': 4,
        'batch_item_count': 10,
    }
}


