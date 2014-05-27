# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class CrawlerSongsPkItem(Item):
    movie_url = Field()
    movie_name = Field()
    songs = Field()

