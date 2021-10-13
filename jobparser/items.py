# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    """
    1) Доработать паука в имеющемся проекте, чтобы он формировал item по структуре:
        *Наименование вакансии
        *Зарплата от
        *Зарплата до
        *Ссылку на саму вакансию
        И складывал все записи в БД(любую)
    """
    name = scrapy.Field()  # Наименование вакансии
    salary = scrapy.Field()
    currency = scrapy.Field()
    company = scrapy.Field()
    salary_min = scrapy.Field()  # Зарплата от
    salary_max = scrapy.Field()  # Зарплата до
    link = scrapy.Field()  # Ссылку на саму вакансию
    _id = scrapy.Field()
