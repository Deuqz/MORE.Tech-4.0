import pandas as pd
from source.clean_data import clean_data
from source.vectorize_data import vectorize_data


def preprocess_dataframe(dataframe: pd.DataFrame) -> None:
    dataframe = dataframe.dropna(subset=['header', 'text'])
    dataframe['cleaned_headers'] = clean_data(dataframe['header'].values)
    dataframe['cleaned_text'] = clean_data(dataframe['text'].values)
    dataframe['vectorized_headers'] = vectorize_data(dataframe['cleaned_headers'].values)
    dataframe['vectorized_text'] = vectorize_data(dataframe['cleaned_text'].values)
