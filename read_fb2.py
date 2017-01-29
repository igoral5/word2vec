# -*- coding: utf-8 -*-
'''
Created on 29 янв. 2017 г.
Читает из каталога zip-архивы с файлами fb2 и использует их для тренировки word2vec 
@author: igor
'''
from __future__ import print_function
import os
import zipfile
import xml.etree.cElementTree as etree
import sys
import codecs
import locale
import re
import gensim 
import logging
import readline
import multiprocessing

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


locale.setlocale(locale.LC_ALL, '')
if sys.stdout.encoding is None:
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
if sys.stderr.encoding is None:
    sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr)

class GeneralForm(object):
    """Приводит слово в нормальную форму
    """
    def __init__(self, name_file=None):
        self.words = {}
        if name_file:
            with codecs.open(name_file, encoding='utf-8') as fd:
                for line in fd:
                    for i, word in enumerate(line.strip().split('\t')):
                        word = word.strip().lower()
                        if i == 0:
                            gen_form = word
                        else:
                            self.words[word] = gen_form
    
    def __call__(self, word):
        if word in self.words:
            return self.words[word]
        else:
            return word
        


class Senteces(object):
    """Читает текст из сжатого (zip) формата bf2, разбивает на предложения, 
       приводит слова к основной форме, исключает стоп-слова и т.п.
    """
    def __init__(self, dirname, name_file_general=None, name_file_stop=None):
        self.dirname = dirname
        self.tag_p = 'p'
        self.tag_body = 'body'
        self.template_split = re.compile(r'[\.?!]', flags=re.UNICODE)
        self.general = GeneralForm(name_file_general)
        self.stop_words = set()
        if name_file_stop:
            with codecs.open(name_file_stop, encoding='utf-8') as fd:
                for line in fd:
                    self.stop_words.add(line.strip().lower())
            
    
    def __iter__(self):
        for name_archive in filter(lambda name: os.path.splitext(name)[1].lower() == '.zip', os.listdir(self.dirname)):
            with zipfile.ZipFile(os.path.join(self.dirname, name_archive), 'r') as archive:
                for fname in filter(lambda name: os.path.splitext(name)[1].lower() == '.fb2', archive.namelist()):
                    with archive.open(fname, 'r') as fd:
                        xmlns = None
                        tag_p = self.tag_p
                        tag_body = self.tag_body
                        in_body = False
                        for event, elem in etree.iterparse(fd, events=('start', 'end', 'start-ns', 'end-ns')):
                            if event == 'start':
                                if elem.tag == tag_body and not elem.attrib:
                                    in_body = True
                            elif event == 'end':
                                if elem.tag == tag_body:
                                    in_body = False
                                elif elem.tag == tag_p and in_body:
                                    for sentence in filter(None, self.split_sentence(''.join(elem.itertext()))):
                                        yield sentence
                            elif event == 'start-ns':
                                if xmlns is None:
                                    xmlns = elem[1]
                                    tag_p = '{%s}%s' % (xmlns, self.tag_p)
                                    tag_body = '{%s}%s' % (xmlns, self.tag_body)
                            elif event == 'end-ns':
                                xmlns = None
                                tag_p = self.tag_p
                                tag_body = self.tag_body
    
    def split_sentence(self, text):
        for sentence in self.template_split.split(text):
            yield map(self.general, filter(lambda token: token and token not in self.stop_words, self.split_tokens(sentence)))
    
    @staticmethod
    def split_tokens(text):
        text = text.lower().replace(u'ё', u'e')
        tokens = []
        token = u''
        for letter in text:
            if letter.isalpha() or letter == u'-':
                token += letter
            else:
                if len(token) != 0:
                    tokens.append(Senteces.clear_token(token))
                    token = u''
        if len(token) != 0:
            tokens.append(Senteces.clear_token(token))
        return tokens
    
    @staticmethod
    def clear_token(text):
        if text[0] == u'-':
            text = text[1:]
        if text and text[-1] == u'-':
            text = text[:-1]
        return text
            
        


def main():
    sentences = Senteces('/home/igor/Dropbox/Books/Стивен Кинг/Тёмная башня', 'newscollection_lemma_dict.tsv', 'stop.txt')
    model = gensim.models.Word2Vec(sentences, workers=multiprocessing.cpu_count())
    while True:
        s = raw_input(u'Input: ').decode('utf-8')
        try:
            for word, weight in model.most_similar(positive=s.strip().split(), topn=20):
                print(word, weight)
        except KeyError:
            print(u'Не найдено')
            

if __name__ == '__main__':
    main()
