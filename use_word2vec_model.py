# -*- coding: utf-8 -*-
'''
Created on 31 янв. 2017 г.
Использование word2vec модели
@author: igor
'''
from gensim.models import Word2Vec
import os
import logging
import sys
import readline  # @UnusedImport

program = os.path.basename(sys.argv[0])
logger = logging.getLogger(program)
 
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))

def main():
    if len(sys.argv) != 2:
        logger.error(u'Требуется дополнительный аргумент файл с обученноей моделью')
        sys.exit(1)
    model = Word2Vec.load(sys.argv[1])
    while True:
        try:
            inp = raw_input('Ввод: ').decode('utf-8')
            spl = inp.lower().split(u'|')
            if len(spl) >= 2:
                positive = spl[0].strip().split()
                negative = spl[1].strip().split()
            elif len(spl) == 1:
                positive = spl[0].strip().split()
                negative = []
            else:
                logger.error(u'Пустой ввод')
                continue
            for t in model.most_similar(positive=positive, negative=negative):
                logger.info(u'%s %f', t[0], t[1])
        except KeyError:
            logger.error(u'Не найдено')

if __name__ == '__main__':
    try:
        main()
    except EOFError:
        pass
    except Exception as e:
        logger.exception(e)
        
