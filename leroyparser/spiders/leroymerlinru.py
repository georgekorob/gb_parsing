import scrapy
from scrapy.http import HtmlResponse
from leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super().__init__()
        self.collection_name = query
        self.start_urls = [f'http://leroymerlin.ru/catalogue/{query}/']

    def parse(self, response: HtmlResponse):
        links = response.xpath('//div[@aria-label="Pagination"]//a')
        for link in links:
            yield response.follow(link, callback=self.parse)
        links = response.xpath('//div[@data-qa-product]/a')
        for link in links:
            yield response.follow(link, callback=self.parse_card)

    def parse_card(self, response: HtmlResponse):
        """
        Реализуйте очистку и преобразование данных с помощью ItemLoader. Цены должны быть в виде числового значения.
        """
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('photos', '//picture[@slot="pictures"]/source[1]/@srcset')
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//uc-pdp-price-view/meta[@itemprop="price"]/@content')
        loader.add_xpath('specification', '//dl/div/*/text()')
        yield loader.load_item()
