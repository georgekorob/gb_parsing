import requests
from lxml import html
from pprint import pprint
import pymongo

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/94.0.4606.61 Safari/537.36'}

response = requests.get("https://yandex.ru/news/")
dom = html.fromstring(response.text)
items = dom.xpath("//div[contains(@class,'mg-grid__col_xs') and not(contains(@class,'_sm_'))]")

client = pymongo.MongoClient('localhost', 27017)
db = client['news_database']
news = db.news

for item in items:
    new = {}
    link = item.xpath(".//a[@class='mg-card__link']/@href")
    if not link:
        continue
    new['link'] = link[0]
    header = item.xpath(".//a[@class='mg-card__link']/h2[@class='mg-card__title']/text()")
    new['header'] = ' '.join([s.replace('\xa0', ' ') for s in header])
    info = item.xpath(".//div[contains(@class,'mg-card__annotation')]//text()")
    new['info'] = ' '.join([s.replace('\xa0', ' ') for s in info])
    new['source'] = item.xpath(".//span[contains(@class,'mg-card-source__source')]//text()")[0]
    new['time'] = item.xpath(".//span[contains(@class,'mg-card-source__time')]//text()")[0]

    if new['link']:
        try:
            news.update_one({'link': new['link']}, {'$set': new}, upsert=True)
        except pymongo.errors.DuplicateKeyError:
            continue

for new in news.find({'source': 'ТАСС'}):
    pprint(new)
