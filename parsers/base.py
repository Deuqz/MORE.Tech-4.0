import datetime
from bs4 import BeautifulSoup


class News:
    def __init__(self, tag, site, header, date, views=None):
        self.tag = tag
        self.site = site
        self.header = header
        self.date = date
        self.views = views

    def __str__(self):
        return str(self.__dict__)


class Parser:
    SITE = None
    def parse_news(self, soup: BeautifulSoup) -> [News]:
        raise NotImplementedError()



def parse_site(parser_class, html_source):
    parser = parser_class()
    if html_source is not None:
        response = BeautifulSoup(html_source, 'html.parser')

        news = parser.parse_news(response)
    else:
        news = parser.parse_news(None)
    return news


