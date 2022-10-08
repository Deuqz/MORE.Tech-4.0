from collections import defaultdict
from itertools import chain

import pandas as pd
import os


def get_datasets(tag: (str | None) = None):
    content = os.listdir('../data')
    content = ['../data/' + path for path in content if '.csv' in path]
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

