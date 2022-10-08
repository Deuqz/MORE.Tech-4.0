import concurrent.futures
from parsers.parsers import KlerkRuParser, LentaRuParser
import csv
from concurrent.futures import ThreadPoolExecutor
# debug tool
def parse_news_month(parser_class):
    parser = parser_class()
    news = parser.get_news_timed()
    with open(f'news{type(parser).__name__}.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(list(news[0].__dict__.keys()))
        for nw in news:
            writer.writerow(nw.to_array())


def run_parse():
    parse_news_month(KlerkRuParser)
    parse_news_month(LentaRuParser)


if __name__ == '__main__':
    run_parse()