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
    TAGS_TO_REMOVE_FROM_MOVIE_NAME = ["download", "songs", "mp3"]

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
        song_info = {}
        for sub_selector in sel.xpath("//table[@class='%s']//a" % SongsPkSpider.OLD_VERSION_TABLE):
            song_url, song_name = self._process_song_name(sub_selector, SongsPkSpider.OLD_VERSION_TABLE)
            if song_url != None and song_name != None:
                song_info[song_url] = song_name
            yield_value = True

        if yield_value:
            yield_value = False
            value = CrawlerSongsPkItem()
            value["movie_url"] = response.request.url
            value["movie_name"] = self._process_movie_name(sel.xpath("//title/text()").extract()[0])
            value["songs"] = song_info
            yield value

        song_info = {}
        for sub_selector in sel.xpath("//li[@class='%s']//li//div[@class='song-title']//a" % SongsPkSpider.NEW_VERSION_TABLE):
            song_url, song_name = self._process_song_name(sub_selector, SongsPkSpider.NEW_VERSION_TABLE)
            song_info[song_url] = song_name
            yield_value = True

        if yield_value:
            yield_value = False
            value = CrawlerSongsPkItem()
            value["movie_url"] = response.request.url
            value["movie_name"] = self._process_movie_name(sel.xpath("//title/text()").extract()[0])
            value["songs"] = items
            yield value

    def _process_song_name2(self, sub_selector, data_version):
            return sub_selector.xpath("@href").extract()[0], sub_selector.xpath("text()").extract()[0].strip()

    def _process_song_name(self, sub_selector, data_version):
        url = None
        name = None
        try:
            url = sub_selector.xpath("@href").extract()[0]
            name = sub_selector.xpath("text()").extract()[0].strip()
        except IndexError as IE:
            print IE
            print sub_selector.extract()
        return url, name

    def _process_movie_name(self, movie_name):
        # movie_name is of the form "Songs.pk - SOMENAME download songs, xx, xx, xx" OR
        # "Songs.pk - SOMENAME, xx, xx, xx"
        best_possible_movie_name = []
        probable_movie_name = movie_name.split(",")[0]
        more_probable_movie_name = probable_movie_name
        split1 = probable_movie_name.split("-")
        if len(split1) > 1:
            more_probable_movie_name = split1[1].strip()
        # split on white space
        splits = list(reversed(more_probable_movie_name.split()))
        # check if the splits now have extra tags to remove, mostly at the end of the list
        i = 0
        for i, val in enumerate(splits):
            if val.lower() not in SongsPkSpider.TAGS_TO_REMOVE_FROM_MOVIE_NAME:
                break
        best_possible_movie_name = splits[i:]
        return " ".join(reversed(best_possible_movie_name)).lower()
