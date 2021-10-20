# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class InstaparserItem(scrapy.Item):
    user_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    profile_pic_url = scrapy.Field()
    follower_count = scrapy.Field()
    following_count = scrapy.Field()
    public_email = scrapy.Field()
    parent = scrapy.Field()
    type = scrapy.Field()
    path = scrapy.Field()
    _id = scrapy.Field()
