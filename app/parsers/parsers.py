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
        if day > 31:
            print(day)
    except:
        return datetime.date.today()

    month = get_month(monthes, splited_date[1])
    try:
        year = int(splited_date[2])
    except:
        year = datetime.date.today().year

    try:
        res = datetime.datetime(year=year, day=day, month=month)
    except:
        raise
    if res > datetime.datetime.today():
        res = datetime.datetime(year=datetime.date.today().year - 1, day=day, month=month)
    return res


class ConsultantRuParser(Parser):
    SITE = 'https://www.consultant.ru'

    def __init__(self):
        super(ConsultantRuParser).__init__()

    def get_news_timed(self, delta_time=None, get_text=False):
        news = []

        for delta in range(100):
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(self.get_page_news, delta * 15 + i + 1, get_text) for i in range(15)]
                for future in concurrent.futures.as_completed(futures):
                    nw = future.result()
                    news += nw
            if news[-1].date < datetime.datetime.combine(datetime.date.today() - delta_time,
                                                         datetime.datetime.min.time()):
                return news
            print(len(news))
        return news

    def get_page_news(self, page_num, get_text=False):
        soup = BeautifulSoup(requests.get(self.SITE+f'/legalnews/?page={page_num}').text, 'html.parser')
        return self.parse_news(soup, get_text=get_text)

    def get_text(self, url):
        soup = BeautifulSoup(requests.get(url).text,
                             'html.parser')
        page = soup.select_one(r'[class="news-page"]')
        try:
            content = page.select_one(r'[class="news-page__content"]')
            text = content.text
            return text
        except:
            print(page)
            raise
    def parse_news(self, soup: BeautifulSoup, get_text=False) -> [News]:
        items = soup.find_all('div', attrs={'class': "listing-news__item"})
        news = []
        for item in items:
            try:
                header = item.select_one(r'[class="listing-news__item-title"]')
                link = header['href']
                date = parse_string_into_date(str(item.select_one(r'[class="listing-news__item-date"]').string))
                text_url = self.SITE+link
                if get_text:
                    news.append(News(tag="accountant", site='conslutant', header=header.span.string, date=date, views=None,
                                     link=text_url, text=self.get_text(text_url)))
                else:
                    news.append(News(tag="accountant", site='conslutant', header=header.span.string, date=date, views=None,
                                     link=text_url, text=None))
            except:
                raise
        return news


class RiaRuParser(Parser):
    SITE = 'https://ria.ru/'

    def __init__(self, type_='accountant'):
        super(RiaRuParser).__init__()
        if type_ == 'accountant':
            self.suffix = 'economy/'
        else:
            self.suffix = ''

    def get_filename(self):
        return f'news{type(self).__name__}{"Economy" if self.suffix == "economy/" else "NonCore"}'

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
            print('news', len(news))
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
        soup = BeautifulSoup(requests.get(self.SITE + self.suffix + f'{date.year}{month}{day}').text,
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
                    print(nxt_url)
                except:
                    break
            if nxt_url is None:
                break
            try:
                nxt = requests.get(self.SITE+nxt_url)
            except:
                break
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
                if views.string is None:
                    views = 0
                else:
                    views = views.string
                news_date = item.select_one(r'[class="list-item__date"]').text
                news_date = parse_string_into_date(news_date)
                text_url = header['href']
                tag = 'none-core' if self.suffix != 'economy/' else 'accountant'
                if kwargs.get('get_text'):
                    try:
                        news.append(News(tag=tag, site='ria', header=header.string, date=news_date, views=views,
                                         link=text_url, text=self.get_text(text_url)))
                    except:
                        continue
                else:
                    news.append(News(tag=tag, site='ria', header=header.string, date=news_date, views=views, link=text_url))
            return news


class KlerkRuParser(Parser):

    def parse_news(self, soup: BeautifulSoup, get_text=None) -> [News]:
        articles = soup.select(r'[class="feed-item feed-item--normal"]')
        news = []
        for article in articles:
            header = article.select_one(r'[class="feed-item__link feed-item-link__check-article"]')
            views = int(article.select_one(r'[class="stat"]').find('core-count-format')['count'])
            date = parse(article.select_one(r'[class="feed-item__stats"]').span.find('core-date-format')['date'])
            text_url = self.SITE + article.select_one(r'[class="feed-item__link feed-item-link__check-article"]')[
                'href']

            if get_text:
                text = self.get_text(text_url)
                news.append(News(tag="accountant", site='klerkru', header=header.string, date=date, views=views,
                                 link=text_url, text=text))
            else:
                news.append(News(tag="accountant", site='klerkru', header=header.string, date=date, views=views,
                                 link=text_url, text=None))
        return news

    SITE = 'https://www.klerk.ru'

    def get_news_timed(self, get_text=False, delta_time=datetime.timedelta(days=30)):
        news = []

        for delta in range(100):
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(self.get_page_news, delta * 15 + i+1, get_text) for i in range(15)]
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
            raise Exception('text not found')
        return text.text

    def get_page_news(self, page_num, get_text=False):
        soup = BeautifulSoup(requests.get(self.SITE + f'/buh/news/page/{page_num}').text,
                             'html.parser')
        return self.parse_news(soup, get_text)


class KommersantParser(Parser):
    SITE = 'https://www.kommersant.ru/archive/rubric/4'

    def get_filename(self):
        return f'news{type(self).__name__}'

    def get_news_timed(self, get_text=False, delta_time=datetime.timedelta(days=30)):
        news = []
        for delta in range((delta_time.days + 14) // 15):
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(self.get_one_day_news,
                                           datetime.date.today() - datetime.timedelta(days=delta * 15 + i),
                                           get_text=get_text)
                           for i in range(15)]
                for future in concurrent.futures.as_completed(futures):
                    nw = future.result()
                    news += nw
            print('news', len(news))
        return news

    def get_views_and_text(self, url):
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        page = soup.select_one(r'[class="lenta_top_doc"]')
        text = page.find('div',
                         attrs={
                             'class': 'doc__body article_text_wrapper js-search-mark'
                         }).select(r'[class="doc__text"]')

        text = ''.join(i.text for i in text)
        views = None
        return views, text

    def parse_news(self, soup: BeautifulSoup, **kwargs) -> [News]:
        body = soup.select_one(r'[class="rubric_lenta"]')
        articles = body.find_all('article', attrs={'class': 'uho rubric_lenta__item js-article'})
        news = []
        for item in articles:
            header = item['data-article-title']
            date = item.select_one(r'[class="uho__tag rubric_lenta__item_tag hide_desktop"]').string.split(',')[0].split('.')
            date = datetime.date(year=int(date[2]), day=int(date[0]), month=int(date[1]))
            url = item['data-article-url']
            views = None
            if kwargs.get('get_text'):
                views, text = self.get_views_and_text(url)
                news.append(News(tag='business', site='kommersant', header=header, date=date,
                                 views=views, link=url, text=text))
            else:
                news.append(News(tag='business', site='kommersant', header=header, date=date, views=views,
                                 link=url, text=None))
        return news

    def get_one_day_news(self, date: datetime.date, get_text=False):
        day = str(date.day)
        if len(day) == 1:
            day = '0' + day
        month = str(date.month)
        if len(month) == 1:
            month = '0' + month
        soup = BeautifulSoup(requests.get(self.SITE+f'/day/{date.year}-{month}-{day}').text,
                             'html.parser')
        return self.parse_news(soup, get_text=get_text)


class TinkoffParser(Parser):
    SITE = 'https://journal.tinkoff.ru/'

    def parse_news(self, soup: BeautifulSoup, get_text=None) -> [News]:
        page = soup.select_one(r'[class="content---3kpa12"]')
        items = page.select(r'[class="item--HDDKc"]')
        news = []
        cnt = 0
        date = None
        for item in items:
            header_info = item.select_one(r'[class="header--RPV23"]')
            try:
                header = header_info.select_one(r'[class="link--xmoGM"]')
                meta = header_info.select_one(r'[class="nowrap--qgOuU"]')
                date = parse(meta.time['datetime'])
                views = meta.select_one(r'[class="counter--F0kEv"]').text[:-1]
            except:
                continue
            try:
                views = int(views)
            except:
                views = int(views[:-1])*1000
            text_url = self.SITE + header['href']
            if get_text:
                news.append(News(tag='business', site='tjournal', header=header.text, date=date, views=views,
                                 link=text_url, text=self.get_text(text_url)))
            else:
                news.append(News(tag='business', site='tjournal', header=header.text, date=date, views=views,
                                 link=text_url, text=None))
        if len(news) == 0:
            raise Exception(date)
        return news

    def get_text(self, url):
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        text = soup.select_one(r'[class="article-body"]').text
        return text

    def get_news_timed(self, delta_time=None, get_text=None):
        news = []

        for delta in range(300):
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(self.get_page_news, delta * 15 + i+1, get_text) for i in range(15)]
                for future in concurrent.futures.as_completed(futures):
                    nw = future.result()
                    news += nw
            print(datetime.datetime.combine(datetime.date.today() - delta_time,
                                                         datetime.datetime.min.time()))
            if news[-1].date < datetime.datetime.combine(datetime.date.today() - delta_time,
                                                         datetime.datetime.min.time()):
                return news
            print(len(news))
        return news

    def get_page_news(self, page_num, get_text):
        try:
            soup = BeautifulSoup(requests.get(self.SITE+f'flows/business-all/page/{page_num}').text, 'html.parser')
        except:
            print(page_num)
            raise
        return self.parse_news(soup, get_text)
