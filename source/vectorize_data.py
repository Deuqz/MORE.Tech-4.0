from typing import List
import pickle
import numpy as np


def vectorize_data(clean_texts: List[str]) -> np.array:
    with open('../models/transformer_model.pickle', 'rb') as f:
        transformer_model = pickle.load(f)
    return transformer_model.encode(clean_texts)