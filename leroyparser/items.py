# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def spec_dic(value):
    """
    2) Написать универсальный обработчик характеристик товаров, который будет формировать данные вне зависимости
    от их типа и количества.
    """
    value = value.strip()
    try:
        if value.isdigit():
            return int(value)
        elif value.replace('.', '').isdigit():
            return float(value)
        else:
            return value
    except Exception as e:
        print(e)
        return value


def clear_price(value):
    try:
        return float(value)
    except Exception as e:
        print(e)


class LeroyparserItem(scrapy.Item):
    """
    1) Взять любую категорию товаров на сайте Леруа Мерлен. Собрать следующие данные:
        ● название;
        ● все фото;
        ● ссылка;
        ● цена.
    """
    name = scrapy.Field(output_processor=TakeFirst())  # название
    photos = scrapy.Field()  # все фото
    link = scrapy.Field(output_processor=TakeFirst())  # ссылка
    price = scrapy.Field(input_processor=MapCompose(clear_price), output_processor=TakeFirst())  # цена
    specification = scrapy.Field(input_processor=MapCompose(spec_dic))  # характеристики
    _id = scrapy.Field()
