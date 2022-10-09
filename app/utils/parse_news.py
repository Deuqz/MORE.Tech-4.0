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


def run_parse_all(days=30):
    parse_news_timed(ConsultantRuParser, get_text=True, time_=datetime.timedelta(days=days))
    parse_news_timed(RiaRuParser, 'none-core', get_text=True, time_=datetime.timedelta(days=days))
    parse_news_timed(KlerkRuParser, get_text=True, time_=datetime.timedelta(days=days))
    parse_news_timed(RiaRuParser, 'accountant', get_text=True, time_=datetime.timedelta(days=days))
    parse_news_timed(KommersantParser, get_text=True, time_=datetime.timedelta(days=days))
    parse_news_timed(TinkoffParser, get_text=True, time_=datetime.timedelta(days=days))
    content = os.listdir('data/temp')
    content = ['data/temp/' + path for path in content if '.csv' in path]
    counter = 1
    for file in content:
        dataframe = pd.read_csv(file)
        dataframe = preprocess_dataframe(dataframe)
        dataframe.to_csv('data/dataset_{0}.csv'.format(counter), index=False)
        counter += 1
    print('parse finished')
