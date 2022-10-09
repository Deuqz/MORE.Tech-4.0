import datetime

import requests
from bs4 import BeautifulSoup
import nltk
from source.preprocess_dataframe import preprocess_dataframe
from parsers.parsers import KlerkRuParser, RiaRuParser, KommersantParser, TinkoffParser, ConsultantRuParser
import csv
import pandas as pd
import os
import argparse

# debug tool


def parse_news_timed(parser_class, tag=None, get_text=False, time_=datetime.timedelta(days=30)):
    if tag is not None:
        parser = parser_class(tag)
    else:
        parser = parser_class()
    news = parser.get_news_timed(get_text=get_text, delta_time=time_)
    if get_text:
        suffix = 'WithText'
    else:
        suffix = 'WithoutText'
    with open('data/temp/'+parser.get_filename() + f'{suffix}.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(list(news[0].__dict__.keys()))
        for nw in news:
            writer.writerow(nw.to_array())
    return parser.get_filename() + f'{suffix}.csv'


def run_parse_all():
    # print(0)
    # parse_news_timed(ConsultantRuParser, get_text=True, time_=datetime.timedelta(days=30))
    # print(1)
    # parse_news_timed(RiaRuParser, 'none-core', get_text=True, time_=datetime.timedelta(days=30))
    # print(2)
    # parse_news_timed(KlerkRuParser, get_text=True, time_=datetime.timedelta(days=30))
    # print(2.5)
    # parse_news_timed(RiaRuParser, 'accountant', get_text=True, time_=datetime.timedelta(days=30))
    # print(3)

    parse_news_timed(KommersantParser, get_text=True, time_=datetime.timedelta(days=30))
    print(4)
    parse_news_timed(TinkoffParser, get_text=True, time_=datetime.timedelta(days=30))
    print(5)
    content = os.listdir('data/temp')
    content = ['data/temp/' + path for path in content if '.csv' in path]
    counter = 1
    for file in content:
        dataframe = pd.read_csv(file)
        dataframe = preprocess_dataframe(dataframe)
        dataframe.to_csv('data/dataset_{0}.csv'.format(counter))
        counter += 1


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
    nltk.download('stopwords')

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
