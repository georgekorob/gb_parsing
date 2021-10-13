# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy1310

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item = self.hhru_process_item(item)
        elif spider.name == 'sjru':
            item = self.sjru_process_item(item)
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def hhru_process_item(self, item):
        item['company'] = ' '.join([c.strip().replace('\xa0', '') for c in item['company']])
        salary = item['salary']
        item['salary_min'], item['salary_max'], item['currency'] = None, None, None
        salary = [s.strip().replace('\xa0', '') for s in salary]
        if len(salary) > 1:
            if 'от' in salary:
                item['salary_min'] = int(salary[salary.index('от') + 1])
            if 'до' in salary:
                item['salary_max'] = int(salary[salary.index('до') + 1])
            item['currency'] = salary[-2]
        del item['salary']

        return item

    def sjru_process_item(self, item):
        item['name'] = ' '.join(item['name'])
        salary = item['salary']
        item['salary_min'], item['salary_max'], item['currency'] = None, None, None
        salary[-1:] = salary[-1].rsplit('\xa0', 1)
        salary = [s for s in [s.replace('\xa0', '') for s in salary] if s]
        if len(salary) > 1:
            if 'от' in salary:
                item['salary_min'] = int(salary[salary.index('от') + 1])
            if 'до' in salary:
                item['salary_max'] = int(salary[salary.index('до') + 1])
            item['currency'] = salary[-1]
            if item['salary_min'] is None and item['salary_max'] is None:
                item['salary_min'] = int(salary[0])
                item['salary_max'] = int(salary[1])
        del item['salary']
        return item
