import datetime

from bs4 import BeautifulSoup
from dateutil.parser import parse
from parsers.base import Parser, News
import requests
import concurrent.futures

def parse_string_into_date(string: str):
    def get_month(monthes, month):
        for month_num in range(len(monthes)):
            if monthes[month_num] == month or monthes[month_num]+',' == month:
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
    try:
        day = int(splited_date[0])
    except:
        return datetime.date.today()

    month = get_month(monthes, splited_date[1])
    res = datetime.datetime(year=datetime.date.today().year, day=day, month=month)
    if res > datetime.datetime.today():
        res = datetime.datetime(year=datetime.date.today().year - 1, day=day, month=month)
    return res

class ConsultantRuParser(Parser):
    SITE = 'https://www.consultant.ru/legalnews/buh/'

    def __init__(self):
        super(ConsultantRuParser).__init__()


    def parse_news(self, soup: BeautifulSoup) -> [News]:
        if soup is None:
            soup = BeautifulSoup(requests.get(self.SITE, allow_redirects=True).text, 'html.parser')

        items = soup.find_all('div', attrs={'class': "listing-news__item"})
        news = []
        for item in items:
            header = item.select_one(r'[class="listing-news__item-title"]').span.string
            date = parse_string_into_date(str(item.select_one(r'[class="listing-news__item-date"]').string))
            news.append(News(tag="accountant", site='consltant', header=header, date=date, views=None))
        return news


class LentaRuParser(Parser):
    SITE = 'https://ria.ru'

    def get_news_timed(self, get_text=False, delta_time=datetime.timedelta(days=30)):
        news = []
        for delta in range((delta_time.days+14) // 15):
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(self.get_one_day_news,
                                           datetime.date.today() - datetime.timedelta(days=delta * 15 + i), get_text=get_text)
                           for i in range(15)]
                for future in concurrent.futures.as_completed(futures):
                    nw = future.result()
                    news += nw
            print(len(news))
        return news

    def get_text(self, url):
        soup = BeautifulSoup(requests.get(url).text,
                             'html.parser')
        page = soup.select_one(r'[class="page__bg"]')
        content = page.select_one(r'[class="article__body js-mediator-article mia-analytics"]')
        text = content.select(r'[class="article__text"]')
        res = []
        for block in text:
            res.append(block.text)
        return ''.join(res)

    def get_one_day_news(self, date: datetime.date, get_text=False):
        day = str(date.day)
        if len(day) == 1:
            day = '0' + day
        month = str(date.month)
        if len(month) == 1:
            month = '0' + month
        soup = BeautifulSoup(requests.get(self.SITE + f'/{date.year}{month}{day}').text,
                             'html.parser')

        news = self.parse_news(soup, date=date, get_text=get_text)
        all_day_news = news.copy()
        while len(news) > 0:
            nxt_url = soup.select_one(r'[class="list-more"]')
            if nxt_url is not None:
                nxt_url = nxt_url['data-url']
            else:
                try:
                    nxt_url = soup.select_one(r'[class="list-items-loaded"]')['data-next-url']
                except:
                    break
            if nxt_url is None:
                break
            nxt = requests.get(self.SITE+nxt_url)
            soup = BeautifulSoup(nxt.text, 'html.parser')
            news = self.parse_news(soup, date=date, get_text=get_text)
            all_day_news += news
            if len(news) == 0 or datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=1), datetime.datetime.min.time()):
                return all_day_news
        return all_day_news

    def parse_news(self, soup: BeautifulSoup, **kwargs) -> [News]:
            items = soup.select(r'[class="list-item"]')
            news = []
            for item in items:
                header = item.select_one(r'[class="list-item__title color-font-hover-only"]')

                views = item.find_next('div',
                                       attrs={'class': "list-item__info"}).select_one(r'[class="list-item__views-text"]')
                if views is None:
                    views = 0
                else:
                    views = int(views.string)
                news_date = item.select_one(r'[class="list-item__date"]').text
                news_date = parse_string_into_date(news_date)
                text_url = header['href']
                if kwargs.get('get_text'):
                    news.append(News(tag="business", site='ria', header=header.string, date=news_date, views=views,
                                     link=text_url, text=self.get_text(text_url)))
                else:
                    news.append(News(tag="business", site='ria', header=header.string, date=news_date, views=views, link=text_url))
            return news


class KlerkRuParser(Parser):

    SITE='https://www.klerk.ru'

    def get_news_timed(self, get_text=False, delta_time=datetime.timedelta(days=30)):
        news = []

        for delta in range(1, 100):
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(self.get_page_news, delta * 15 + i, get_text) for i in range(15)]
                for future in concurrent.futures.as_completed(futures):
                    nw = future.result()
                    news += nw
            if news[-1].date < datetime.datetime.combine(datetime.date.today() - delta_time, datetime.datetime.min.time()):
                return news
        return news

    def get_text(self, url):
        soup = BeautifulSoup(requests.get(url).text,
                             'html.parser')
        page = soup.select_one(r'[class="article"]')
        text = page.select_one(r'[class="article__content"]')
        if text is None:
            return "Text not found"
        return text.text

    def get_page_news(self, page_num, get_text=False):
        soup = BeautifulSoup(requests.get(self.SITE + f'/buh/news/page/{page_num}').text,
                             'html.parser')
        articles = soup.select(r'[class="feed-item feed-item--normal"]')
        news = []
        for article in articles:
            header = article.select_one(r'[class="feed-item__link feed-item-link__check-article"]')
            views = int(article.select_one(r'[class="stat"]').find('core-count-format')['count'])
            date = parse(article.select_one(r'[class="feed-item__stats"]').span.find('core-date-format')['date'])
            text_url = self.SITE + article.select_one(r'[class="feed-item__link feed-item-link__check-article"]')['href']

            if get_text:
                text = self.get_text(text_url)
                news.append(News(tag="accountant", site='klerkru', header=header.string, date=date, views=views,
                                 link=text_url, text=text))
            else:
                news.append(News(tag="accountant", site='klerkru', header=header.string, date=date, views=views,
                                 link=text_url))
        return news

class GlavBukhParser(LentaRuParser):
    SITE = 'https://www.glavbukh.ru/news'

    def parse_news(self, soup: BeautifulSoup) -> [News]:
        pass

    def get_news_timed(self, delta_time=None):
        pass