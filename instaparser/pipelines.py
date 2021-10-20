# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
import pymongo


class InstaparserPipeline:
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        self.mongo_base = client.instabase

    def process_item(self, item, spider):
        try:
            self.mongo_base.users.insert_one(item)
        except pymongo.errors.DuplicateKeyError:
            print('Такой пользователь уже существует!')


class InstaparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['profile_pic_url']:
            try:
                yield scrapy.Request(item['profile_pic_url'])
            except Exception as e:
                print(e)

    def file_path(self, request, response=None, info=None, *, item=None):
        item_name = item['username']
        win_symbols = ['/', '\\', '>', '<', ':', '«', '|', '*', '?', '»']
        for s in win_symbols:
            item_name = item_name.replace(s, '').strip()
        item['path'] = f'{item["parent"]}/{item_name} {item["user_id"]}.jpg'
        return item['path']
