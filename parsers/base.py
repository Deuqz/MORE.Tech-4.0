import datetime
from bs4 import BeautifulSoup


class News:
    def __init__(self, tag, site, header, date, views, link, text=None):
        self.tag = tag
        self.site = site
        self.header = header
        self.date = date
        self.views = views
        self.link = link
        if text is not None:
            self.text = text

    def to_array(self):
        return list(self.__dict__.values())


class Parser:
    SITE = None

    def parse_news(self, soup: BeautifulSoup) -> [News]:
        raise NotImplementedError()

    def get_news_timed(self, delta_time=None):
        raise NotImplementedError()


