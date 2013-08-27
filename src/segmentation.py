# -*- coding: utf8 -*-
import re
import redis
import cPickle

REAL_WORD_KEY = 'store.key.real_words'
FAKE_WORD_KEY = 'store.key.fake_words'

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
pipe = r.pipeline(transaction=False)


class Words:
    REAL_WORD_KEY = 'store.key.real_words'
    FAKE_WORD_KEY = 'store.key.fake_words'
    dictionary_path = 'yyx_segmentation_dictionary'
    MAX_LENGTH = 7
    TOTAL_COUNT = -1

    variance = lambda self, avg_num, data_list: sum([(data - avg_num)**2 for data in data_list]) / len(data_list)
    create_new_word = lambda self, *x: u''.join(x)
    match_word = lambda self, in_str: in_str in self.DICTIONARY

    def __init__(self):
        self.DICTIONARY = cPickle.load(open(self.dictionary_path, 'r'))
        self.TOTAL_COUNT = int(r.get('segmentation.count'))
        if self.TOTAL_COUNT is None:
            self.TOTAL_COUNT = 0

    def __del__(self):
        '''store total_count and dictionary'''
        r.set('segmentation.count', self.TOTAL_COUNT)
        cPickle.dump(self.DICTIONARY, open(self.dictionary_path, 'w'))

    def _get_frequency(self, words):
        '''get words frequency from db
        Parameter:
            words: a list of word
        TODO: can use redis to store the frequency
        '''
        frequency =  [f if f else 0 for f in r.hmget(self.REAL_WORD_KEY, *words)]
        return frequency

    def _get_probablity(self, words):
        return [i / self.TOTAL_COUNT for i in self._get_frequency(words)]

    def _get_frequency_new_words(self, new_words):
        '''get fake words frequency from db
        Parameter:
            words: a list of word
        '''
        frequency = [f if f else 0 for f in r.hmget(self.FAKE_WORD_KEY, *words)]
        return frequency

    def _get_probablity_new_words(self, new_words):
        return [i / self.TOTAL_COUNT for i in self._get_frequency_new_words(words)]

    def _update_words_frequency(self, words):
        '''update words frequency from db
        params:
            words: a list for words
        '''
        def update_words_transaction(pipe, words):
            word_list = words.keys()
            frequency = zip(word_list, get_frequency(word_list))
            for key, value in frequency:
                words[key] += value
            pip.multi()
            pipe.hmset(self.REAL_WORD_KEY, words)

        word_count = dict()
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        r.transaction(update_words_transaction, word_count)
    
    def _add_words(self, words):
        '''add word to word dictionary
        params:
            words: a dict like:{word:frequency}
        '''
        pipe.hmset(self.REAL_WORD_KEY, words)
        self.DICTIONARY.update(words.keys())
        pipe.hdel(self.FAKE_WORD_KEY, *words.keys())
        pipe.execute()

    def _update_new_words_frequency(self, words):
        '''update new words frequency
        params:
            words: a dict like:{word:frequency}
        '''
        pipe.hmset(self.FAKE_WORD_KEY, words)
        pipe.execute()

    def leaning(self, words):
        '''analysic words and find the new words
        params:
            words: a list for words
        '''
        l = [len(i) for i in words]
        new_words_count = dict()
        new_words_dict = dict()
        count = 0
        length = len(words)
        while (count < length):
            wl = l[count]
            t = count
            while wl < self.MAX_LENGTH:
                t += 1
                wl += l[t]
            if t != count:
                new_word = self.create_new_word(words[count:t+1])
                new_words_dict[new_word] = (self.create_new_word(words[count:t]), words[t])
                new_words_count[new_word] = new_words_count.get(new_word) + 1
            count += 1
        # now we have got all new words.
        new_words = new_words_count.keys()
        new_words_frequency = self._get_frequency_new_words(new_words)
        real_words = dict()
        for word, frequency in zip(new_words, new_words_frequency):
            new_words_count[word] += frequency
            if new_words_count[word] > 1000:
                # when the count above 1000, we shoud check does it is a real new word
                if self._check_probablity(new_words_count[word], new_words_dict[word]):
                    real_words[word] = new_words_count[word]
                    # self._add_words(word, new_words_count[word])
                    del new_words_count[word]
        # update words frequency
        print new_words_count
        print real_words
        # self._update_new_words_frequency(new_words_count)
        # self._add_words(real_words)

    def _check_probablity(self, word, frequency, l):
        '''check does it is a real word'''
        probablitys = dict(zip(l, self._get_probablity(l)))
        p = (float(frequency) / self.TOTAL_COUNT) / probablitys[0]
        if p > probablitys[0] and p > probablity[1]:
            return True
        return False

    def analysic(self, words):
        '''return the probablity for the list of words to composition the sentence
        '''
        pl = self._get_probablity(words)
        p = pl[0]
        for i in range(1, len(pl)):
            if pl[i] == 0: return 0
            p *= (pl[i-1]/pl[i])
        return p

    def segmentation(self, sentence):
        self.TOTAL_COUNT += 1
        length = len(sentence)
        start = length - 1
        end = length
        words_reverse = []
        while start > 0:
            while self.match_word(sentence[start - 1:end]) and start - 1 > 0:
                start -= 1
            words_reverse.append(sentence[start:end])
            end = start
            start -= 1
        words_reverse.append(sentence[start:end])
        words = []
        start = 0
        end = 1
        while end < length:
            while self.match_word(sentence[start:end + 1]) and end + 1 < length:
                end += 1
            words.append(sentence[start:end])
            start = end
            end += 1
        words.append(sentence[start:end])
        l1 = len(words)
        l2 = len(words_reverse)                            
        if l1 > l2:
            return words
        elif l2 > l1:
            return words_reverse
        else:
            avg_l1 = l1 / length
            avg_l2 = l2 / length
            if avg_l1 > avg_l2:
                return words
            elif avg_l2 >avg_l1:
                return words_reverse
            else:
                v1 = self.variance(avg_l1, [len(word) for word in words])
                v2 = self.variance(avg_l2, [len(word) for word in words_reverse])
                if v1 < v2:
                    return words
                elif v2 < v1:
                    return words_reverse
                else:
                    p1 = self.analysic(words)
                    p2 = self.analysic(words_reverse)
                    if p1 > p2:
                        return words
                    else:
                        return words_reverse

_words = Words()
_SPILT_RE = re.compile(u'[,|.|;|\'|\[|\]|{|}|!|@|#|$|%|^|&|*|\\|"|:|`|~|-|_|=|+|。|，|；|‘|“|]')
def segmentation(sentence):
    if not isinstance(sentence, unicode):
        sentence = unicode(sentence, 'utf8')

    l = _SPILT_RE.split(sentence)
    for i in l:print i
    words = []
    for i in l:
        words += _words.segmentation(i.strip())
    return words