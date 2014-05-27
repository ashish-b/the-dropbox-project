# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymongo

class CrawlerSongspkPipeline(object):

    def __init__(self):
        self.pmc = pymongo.MongoClient(USE_REAL_CONNECTION_STRING_HERE_CANT_SUBMIT_TO_PUBLIC_GITHUB)
        self.database = self.pmc.songs_pk
        self.collection = self.database.test

    def _insert_to_db(self, item):
        insert_this = {}
        insert_this['movie_name'] = item['movie_name']
        insert_this['movie_url'] = item['movie_url']
        insert_this['songs'] = item['songs']
        self.collection.insert(insert_this)

    def process_item(self, item, spider):
        self._insert_to_db(item)
        return item

    def __del__(self):
        self.pmc.close()
