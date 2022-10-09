from source.clean_data import clean_data
from source.vectorize_data import vectorize_data
from source.track_repository import get_datasets
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import datetime


def filter_news(tag: str, role: str, role_description: str) -> pd.DataFrame:

    def get_score(row, vector):
        return cosine_similarity([row], [vector])[0][0]

    def get_days(row):
        return row.days

    default_datasets = get_datasets('none-core')
    role_datasets = get_datasets(tag)

    cleaned_role = clean_data([role + ' ' + role_description])
    role_vector = vectorize_data(cleaned_role)[0]

    dataset = pd.concat([default_datasets, role_datasets])
    dataset['date'] = pd.to_datetime(dataset['date'])
    dataset['date_delta'] = datetime.datetime.today() - dataset['date']
    dataset['date_delta'] = dataset['date_delta'].apply(get_days)
    dataset['headers_score'] = dataset['vectorized_headers'].apply(get_score, vector=role_vector)
    dataset['text_score'] = dataset['vectorized_text'].apply(get_score, vector=role_vector)
    dataset = dataset.query('date_delta <= 14')
    dataset = dataset.sort_values(by=['headers_score', 'text_score', 'date_delta', 'views'],
                                  ascending=[False, False, True, False])

    return dataset[['header', 'date', 'link']].head(5)
