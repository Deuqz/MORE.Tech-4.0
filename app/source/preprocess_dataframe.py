import pandas as pd
from source.clean_data import clean_data
from source.vectorize_data import vectorize_data


def preprocess_dataframe(dataframe_: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    dataframe = dataframe_.dropna(subset=['header', 'text'])
    dataframe['cleaned_headers'] = clean_data(dataframe['header'].values, verbose=verbose)
    dataframe['cleaned_text'] = clean_data(dataframe['text'].values, verbose=verbose)
    dataframe['vectorized_headers'] = vectorize_data(dataframe['cleaned_headers'].values, verbose=verbose)
    dataframe['vectorized_text'] = vectorize_data(dataframe['cleaned_text'].values, verbose=verbose)
    return dataframe
