# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
import hashlib
from scrapy.utils.python import to_bytes
from pymongo import MongoClient


class LeroyparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin

    def process_item(self, item, spider):
        """
        2) Написать универсальный обработчик характеристик товаров, который будет формировать данные вне зависимости
        от их типа и количества.
        """
        spec = item['specification']
        item['specification'] = {dt: dd for dt, dd in zip(spec[:-1:2], spec[1::2])}
        self.mongo_base[spider.collection_name].insert_one(item)
        return item


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        """
        3) Реализовать хранение скачиваемых файлов в отдельных папках, каждая из которых должна соответствовать
        собираемому товару
        """
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        item_name = item['name']
        hash_name = hashlib.sha1(to_bytes(item_name)).hexdigest()[-10:]
        win_symbols = ['/', '\\', '>', '<', ':', '«', '|', '*', '?', '»']
        for s in win_symbols:
            item_name = item_name.replace(s, '').strip()
        item_name = ' '.join(item_name.split(' ')[:2]) + ' ' + hash_name
        return f'full/{item_name}/{image_guid}.jpg'
