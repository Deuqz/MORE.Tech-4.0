import datetime

import requests
from bs4 import BeautifulSoup

from parsers.parsers import KlerkRuParser, RiaRuParser, KommersantParser
import csv
import argparse

# debug tool


def parse_news_timed(parser_class, tag=None, get_text=False, time_=datetime.timedelta(days=30)):
    if tag is not None:
        parser = parser_class(tag)
    else:
        parser= parser_class()
    news = parser.get_news_timed(get_text=get_text, delta_time=time_)
    if get_text:
        suffix = 'WithText'
    else:
        suffix = 'WithoutText'
    with open('data/'+parser.get_filename() + f'{suffix}.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(list(news[0].__dict__.keys()))
        for nw in news:
            writer.writerow(nw.to_array())
    return parser.get_filename() + f'{suffix}.csv'


def run_parse_all():
    parse_news_timed(RiaRuParser, 'non-core', get_text=True, time_=datetime.timedelta(days=30))
    parse_news_timed(KlerkRuParser, get_text=True, time_=datetime.timedelta(days=30))
    parse_news_timed(RiaRuParser, 'accountant', get_text=True, time_=datetime.timedelta(days=30))
    parse_news_timed(KommersantParser, get_text=True, time_=datetime.timedelta(days=30))


def get_data(parser_name: str, parser_args: dict, get_text: bool, time_: datetime.timedelta):
    args = []
    if parser_name == 'ria':
        parser_class = RiaRuParser
        args = [parser_args.get('tag')]
    elif parser_name == 'klerkru':
        parser_class = KlerkRuParser

    elif parser_name == 'kommersant':
        parser_class = KommersantParser
    else:
        raise Exception(f'Unknown parser type: {parser_name}')
    filename = parse_news_timed(parser_class, args, get_text, time_)
    print(filename)


if __name__ == '__main__':
    run_parse_all()
    # parser = argparse.ArgumentParser(description='loading news to file')
    # parser.add_argument('--name', type=str,
    #                     help='parser name')
    # parser.add_argument('--tag',
    #                     default=None,
    #                     help='required tag for parser')
    # parser.add_argument('--text', type=str, help='get text from news or not')
    # parser.add_argument('--time', default=30, type=int, help='number of days to parse news')
    #
    # arg = parser.parse_args()
    # print(arg.text)
    # print(get_data(arg.name, arg.tag, get_text=(arg.text == 'True'), time_=datetime.timedelta(days=arg.time)))
    #
    # soup = BeautifulSoup(requests.get('https://www.rbc.ru/business/08/10/2022/634139269a79479a6431ead3').text, 'html.parser')
