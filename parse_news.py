import concurrent.futures
import datetime
import time
from parsers.parsers import KlerkRuParser, LentaRuParser
import csv
# debug tool
def parse_news_month(parser_class, get_text=False):
    parser = parser_class()
    news = parser.get_news_timed(get_text=get_text)
    if get_text:
        suffix = 'WithText'
    else:
        suffix = 'WithoutText'
    with open(f'news{type(parser).__name__}{suffix}.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(list(news[0].__dict__.keys()))
        for nw in news:
            writer.writerow(nw.to_array())


def run_parse():
    time_ = time.time()
    print(0)
    parse_news_month(KlerkRuParser, True)
    print(time.time() - time_)
    print(1)
    parse_news_month(LentaRuParser, True)
    print(time.time() - time_)
    print(2)
    parse_news_month(KlerkRuParser, False)
    print(time.time() - time_)
    print(3)
    parse_news_month(LentaRuParser, False)
    print(time.time() - time_)


if __name__ == '__main__':
    run_parse()