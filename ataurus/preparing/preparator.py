"""
This module contains Preparator class that will prepare the data in DataFrame object.
All unnecessary symbols, stop words and other incorrect symbols will be removed from the text.
"""

import pandas as pd
import re
from razdel import tokenize, sentenize
from .rules import PUNCTUATIONS, URLS


class Preparator:
    def __init__(self):
        self._authors = None
        self._texts = None

    def fit(self, data: pd.DataFrame):
        """
        Methods gets texts and authors from the passed data.
        :param data: DataFrame object containing 'text' and 'author' columns (it can be None)
        :return: self
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("The data isn't instance of pd.DataFrame")

        if not ('text' in data):
            raise KeyError("The input data in .csv format hasn't 'text' column, please fix your file")

        data = data.dropna()
        self._texts = data['text'].to_numpy()

        # It can be test data to predict targets
        if 'author' in data:
            self._authors = data['author'].values

        return self

    @property
    def texts(self):
        return self._texts

    @property
    def authors(self):
        return self._authors

    def tokens(self,
               index: int = None,
               lower=True,
               delete_punctuations=True) -> list:
        """
        Get a list of tokens from the text received by the index from the DataFrame.

        :param index: index of a text of the DataFrame that you want to process.
                      If it's None, all the texts will be processed
        :param lower: to lower a result
        :param delete_punctuations: delete all punctuations from a result
        :return: list - the list of tokens
        """
        results = []
        if index is None:
            index = range(len(self._texts))
        else:
            if not isinstance(index, int):
                raise TypeError("The index that you want to use to get a text isn't int!")
            index = [index]

        for i in index:
            text = self._process_text(i, lower=lower, delete_whitespace=True, delete_urls=True)

            if delete_punctuations:
                tokens = [token.text for token in tokenize(text) if not PUNCTUATIONS.search(token.text)]
            else:
                tokens = [token.text for token in tokenize(text)]
            results.append(tokens)

        return results

    def sentences(self,
                  index: int = None,
                  lower=True,
                  delete_punctuations=True) -> list:
        """
        Get a list of sentences from the text received by the index from the DataFrame.

        :param index: index of a text of the DataFrame that you want to process.
                      If it's None, all the texts will be processed.
        :param lower: to lower a result
        :param delete_punctuations: delete all punctuations from a result
        :return: list - the list of sentences
        """
        results = []
        if index is None:
            index = range(len(self._texts))
        else:
            if not isinstance(index, int):
                raise TypeError("The index that you want to use to get a text isn't int!")
            index = [index]

        for i in index:
            text = self._process_text(i, lower=False, delete_whitespace=False, delete_urls=True)
            if not text:
                continue

            if lower:
                sentences = [sentence.text.lower() for sentence in sentenize(text)]
            else:
                sentences = [sentence.text for sentence in sentenize(text)]

            if delete_punctuations:
                sentences = [re.sub(r'[\s]+', r' ', PUNCTUATIONS.sub(" ", sentence)).strip() for sentence in sentences]

            results.append(sentences)

        return results

    def _process_text(self,
                      index: int,
                      lower=True,
                      delete_whitespace=True,
                      delete_urls=True) -> str:
        """
        Process the text depending on specified options.

        :param index: index of a text of the DataFrame that you want to process
        :param lower: to lower a result
        :param delete_whitespace: remove redundant whitespaces
        :param delete_urls: remove all url links
        :return: str - processed text
        """
        text = self._texts[index]
        if not text:
            return None

        if not isinstance(text, str):
            raise TypeError("Text value is not string")

        if lower:
            text = text.lower()
        if delete_whitespace:
            text = re.sub(r'[\s]+', r' ', text).strip()
        if delete_urls:
            text = URLS.sub('', text)
        return text
