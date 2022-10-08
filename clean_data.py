import re
from nltk.corpus import stopwords
from pymystem3 import Mystem
from tqdm import tqdm
from typing import List


def clean_data(texts: List[str], verbose: bool = False) -> List[str]:
    stem = Mystem()
    len_texts = len(texts)
    russian_stopwords = stopwords.words("russian")
    clean_texts = [[] for _ in range(len_texts)]
    if verbose:
        iterations = tqdm(range(len_texts))
    else:
        iterations = range(len_texts)
    for i in iterations:
        text = texts[i]
        lemmas = stem.lemmatize(text)
        lemmas = [word for word in lemmas if (word not in russian_stopwords) and (word != ' ') and (word != '\n')]
        clean_lemmas = re.sub('[^A-Za-zА-Яа-я\s]', '', ' '.join(lemmas)).lower()
        clean_texts[i] = clean_lemmas
    return clean_texts
