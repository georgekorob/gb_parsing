import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

# pip install scrapy
# scrapy startproject jobparser .
# scrapy genspider hhru hh.ru
# scrapy crawl hhru

class SjruSpider(scrapy.Spider):
    """ 2) Создать в имеющемся проекте второго паука по сбору вакансий с сайта superjob.
    Паук должен формировать item'ы по аналогичной структуре и складывать данные также в БД"""
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4',
                  'https://zelenograd.superjob.ru/vacancy/search/?keywords=python',
                  'https://spb.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[@class='f-test-search-result-item']//a[contains(@href,'/vakansii/')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)


    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//div[@class='_3MVeX']//h1/text()").getall()
        salary = response.xpath("//span[@class='_1h3Zg _2Wp8I _2rfUm _2hCDz']/text()").getall()
        company = response.xpath("//div/a[contains(@href,'/clients/')]/h2/text()").get()
        link = response.url
        item = JobparserItem(name=name, salary=salary, company=company, link=link)
        yield item
