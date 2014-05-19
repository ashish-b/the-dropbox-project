from scrapy.spider import Spider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from ..items import CrawlerSongsPkItem
import re

class SongsPkSpider(Spider):
    name = "songs.pk"
    allowed_domains = ["songs.pk", "songspk.name"]
    start_urls = ["http://songspk.name/bollywood-songs-mp3.html"]
    url_pattern = re.compile("^[a-z]_list\.html|numeric_list\.html")
    OLD_VERSION_TABLE = "greenborder2" #table class
    NEW_VERSION_TABLE = "titlev" #li

    def parse(self, response):
        sel = Selector(response)
        url_base = response.request.url.rpartition("/")[0]

        for url in sel.xpath("//ul[@class='ctlg-holder']//a/@href").extract():
            yield Request(url_base + "/" + url, callback=self.parse_album)

        for url in sel.xpath('//a/@href').extract():
            if SongsPkSpider.url_pattern.match(url):
                yield Request(url_base + "/" + url, callback=self.parse)

    def parse_album(self, response):
        sel = Selector(response)
        url_base = response.request.url.rpartition("/")[0]

        for url in sel.xpath("//ul[@class='ctlg-holder']//a/@href").extract():
            yield Request(url_base + "/" + url, callback=self.parse_album)

        yield_value = False
        items = []
        for song_name in sel.xpath("//table[@class='%s']//a/text()" % SongsPkSpider.OLD_VERSION_TABLE).extract():
            items.append(song_name.strip())
            yield_value = True

        if yield_value:
            yield_value = False
            value = CrawlerSongsPkItem()
            value["movie_name"] = response.request.url
            value["songs"] = items
            yield value

        items = []
        for song_name in sel.xpath("//li[@class='%s']//li//div[@class='song-title']" % SongsPkSpider.NEW_VERSION_TABLE).extract():
            items.append(song_name.strip())
            yield_value = True
        if yield_value:
            yield_value = False
            value = CrawlerSongsPkItem()
            value["movie_name"] = response.request.url
            value["songs"] = items
            yield value
