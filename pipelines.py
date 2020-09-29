
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.pipelines.files import FilesPipeline

import os
import hashlib
import logging
import urllib.parse
import urllib.request, urllib.parse, urllib.error
import psycopg2
logger = logging.getLogger(__name__)

class FirmwarePipeline(FilesPipeline):
    def __init__(self, store_uri, download_func=None, settings=None):

        self.database = psycopg2.connect(database=os.environ['db_database'],
                                          user=os.environ['db_user'],
                                          password=os.environ['db_password'],
                                          host=os.environ['db_host'])
        
        super(FirmwarePipeline, self).__init__(store_uri, download_func, settings)

    @classmethod
    def from_settings(cls, settings):
        store_uri = settings['FILES_STORE']
        cls.expires = settings.getint('FILES_EXPIRES')
        cls.files_urls_field = settings.get('FILES_URLS_FIELD')
        cls.files_result_field = settings.get('FILES_RESULT_FIELD')

        return cls(store_uri, settings=settings)

    # override
    def file_path(self, request, response=None, info=None):
        extension = os.path.splitext(os.path.basename(
            urllib.parse.urlsplit(request.url).path))[1]
        return '%s/%s%s' % (request.meta['vendor'][0],
                            hashlib.sha1(request.url.encode()).hexdigest(), extension)

    def get_media_requests(self, item, info):
        for x in ['vendor', 'firmware']:
            if x not in item:
                raise DropItem(
                    'Missing required filed \'%s\' for item: ' % x)

        # if any(x in url.path for x in ['driver', 'utility', 'install', 'wizard', 'gpl', 'login']):
        #     raise DropItem('Filtered path type: \'%s\'' % url.path)

        # uniqueify
        item[self.files_urls_field] = list(set(item['firmware']))

        return [Request(x, meta={'vendor': item['vendor']}) for x in item[self.files_urls_field]]

    def item_completed(self, results, item, info):
        results = results[0][1]
        release_notes = item.get('releasenotes', None)
        if release_notes:
            release_notes = ' '.join(release_notes)
        version = hashlib.sha1(results['url'].encode()).hexdigest()
        build = hashlib.sha1(results['url'].encode()).hexdigest()

        try:
            c = self.database.cursor()
            c.execute('SELECT id FROM image WHERE hash=%s',
                      (results['checksum'],))
            image_id = c.fetchone()

            if not image_id:
                c.execute('SELECT id FROM brand WHERE name=%s', (item['vendor'][0],))
                brand_id = c.fetchone()

                if not brand_id:
                    c.execute('INSERT INTO brand (name) VALUES (%s) RETURNING id', (item['vendor'][0],))
                    brand_id = c.fetchone()

                c.execute('INSERT INTO image (filename, description, brand_id, hash) VALUES (%s, %s, %s, %s) RETURNING id',
                          (results['path'], item.get('description', None), brand_id, results['checksum']))

                image_id = c.fetchone()
            else:
                c.execute('SELECT filename FROM image WHERE hash=%s',
                          (results['checksum'],))
                path = c.fetchone()
                logger.info('found existing database entry for image: %d!' % image_id)
                if path[0] != results['path']:
                    os.remove(os.path.join(self.store.basedir,
                                           results['url']['path']))
                    logger.info('removing duplicate file: %s!' % results['url']['path'])

            c.execute('SELECT id FROM product WHERE iid=%s AND product IS NOT DISTINCT FROM %s AND version IS NOT DISTINCT FROM %s AND build IS NOT DISTINCT FROM %s',
                      (image_id, item['product'][0], version, build))
            product_id = c.fetchone()

            if not product_id:
                c.execute('INSERT INTO product (iid, url, mib_url, product, version, build, date) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id',
                          (image_id, results['url'], release_notes, item['product'], version, build, None))
                product_id = c.fetchone()
                logger.info('inserted db entry for product: %d!' % product_id)

            else:
                c.execute("UPDATE product SET (iid, url, mib_url, product, version, build, date) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE id=%s",
                          (image_id, results['url'], release_notes, item['product'], version, build, None, image_id))
            self.database.commit()

        except BaseException as e:
            self.database.rollback()
            logger.warning('exception: %s!' % e)
            raise
        finally:
            if self.database and c:
                c.close()

        return item
                    
                              
                    
