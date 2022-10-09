from collections import defaultdict
from itertools import chain

import numpy as np
import pandas as pd
import os


def parse_vector(string: str) -> np.array:
    string = string[1:-1]
    vals_str = string.split()
    return np.array([float(x) for x in vals_str])

def get_datasets(tag = None):
    content = os.listdir('data')
    content = ['data/' + path for path in content if '.csv' in path]
    datasets = defaultdict(list)
    for file in content:
        try:
            dataset = pd.read_csv(file)
            type = dataset.loc[0, 'tag']
            datasets[type].append(dataset)
        except:
            pass
    if tag is None:
        all_datasets = pd.concat(list(chain.from_iterable(list(datasets.values()))))
    else:
        all_datasets = pd.concat(datasets[tag])

    all_datasets['vectorized_headers'] = all_datasets['vectorized_headers'].apply(parse_vector)
    all_datasets['vectorized_text'] = all_datasets['vectorized_text'].apply(parse_vector)
    return all_datasets

def get_all_datasets(tag = None):
    content = os.listdir('data')
    content = ['data/' + path for path in content if '.csv' in path]
    datasets = defaultdict(list)
    for file in content:
        try:
            dataset = pd.read_csv(file)
            type = dataset.loc[0, 'tag']
            datasets[type].append(dataset)
        except:
            pass
    if tag is None:
        all_datasets = pd.concat(list(chain.from_iterable(list(datasets.values()))))
    else:
        all_datasets = pd.concat(datasets[tag])

    return all_datasets
