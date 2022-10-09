from typing import List
import pickle
import numpy as np
from tqdm import tqdm


def vectorize_data(clean_texts: List[str], verbose: bool = False) -> List[np.array]:
    with open('models/transformer_model.pickle', 'rb') as f:
        transformer_model = pickle.load(f)
    result = []
    if verbose:
        iterations = tqdm(clean_texts)
    else:
        iterations = clean_texts
    for text in iterations:
        result.append(transformer_model.encode(text))
    return result
