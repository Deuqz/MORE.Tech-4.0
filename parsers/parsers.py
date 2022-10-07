import datetime

from bs4 import BeautifulSoup

from parsers.base import Parser, News
import requests


class ConsultantRuParser(Parser):
    SITE = 'https://www.consultant.ru/legalnews/buh/'
    def __init__(self):
        super(ConsultantRuParser).__init__()

    def parse_string_into_date(self, string: str):

        def get_month(monthes, month):
            for month_num in range(len(monthes)):
                if monthes[month_num] == month:
                    return month_num+1
            return -1
        string = string.lower()
        if string == 'сегодня':
            return datetime.date.today()
        elif string == 'вчера':
            return datetime.date.today() - datetime.timedelta(days=1)
        splited_date = string.split()
        monthes = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
                   "ноября", "декабря"]
        day = int(splited_date[0])
        month = get_month(monthes, splited_date[1])
        res = datetime.datetime(year=datetime.date.today().year, day=day, month=month)
        if res > datetime.datetime.today():
            res = datetime.datetime(year=datetime.date.today().year - 1, day=day, month=month)
        return res

    def parse_news(self, soup: BeautifulSoup) -> [News]:
        if soup is None:
            soup = BeautifulSoup(requests.get(self.SITE, allow_redirects=True).text, 'html.parser')

        items = soup.find_all('div', attrs={'class': "listing-news__item"})
        news = []
        for item in items:
            header = item.select_one(r'[class="listing-news__item-title"]').span.string
            date = self.parse_string_into_date(str(item.select_one(r'[class="listing-news__item-date"]').string))
            news.append(News(tag="accountant", site='consltant', header=header, date=date, views=None))
        return news


class LentaRuParser(Parser):
    def parse_news(self, soup: BeautifulSoup) -> [News]:
        pass
