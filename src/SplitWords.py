# -*- coding: utf-8 -*-
from string import maketrans


FILE_PATH = 'ch_dict.txt'
WORD_MAX_LENTH = 8
SYMBOL = u',./-[]{}:\'\";+_=\n\t><@!#$%^&*()`~\\|，。；‘“’”：）（！2@#￥%……&*~`·~【】'
REMOVE_NUMBER = 1
REMOVE_ENGLISH = 2
EN_CHARS = u'qwertyuioplkjhgfdsazxcvbnmMNBVCXZASDFGHJKLPOIUYTREWQ'
NUMBER_CHARS = u'1234567890'
class Yyx:
    words_set = set()
    translate_table = None
    parse_type = 0
    def __init__(self, parse_type = 0):
        self._load_words_library()
        block = SYMBOL
        if parse_type & REMOVE_ENGLISH:
            block +=EN_CHARS
        if parse_type & REMOVE_NUMBER:
            block += NUMBER_CHARS
        self.translate_table = maketrans(block, u' '*len(block))
        self.parse_type = parse_type

    def _load_words_library(self):
        try:
            words_str = open(FILE_PATH, 'r').read()
        except Exception, e:
            print 'load words library error.', e
            word_str = ''
        if words_str[:3] == 'BOM':
            words_str = words_str[3:]
        words_str = words_str.decode("gbk")
        self.words_set.update(words_str.split('\n'))
        print 'load %d words'%len(self.words_set)

    def _remove_symbol(self, strs):
        '''remove symbols in string'''
        return strs.translate(self.translate_table)

    def read_from_file(self, file_path, io):
        try:
            file_to_parser = open(file_path, 'r').read()
        except Exception, e:
            print 'load failed, path:%s'%file_path, e
            return
        if not file_to_parser:
            print 'string is None!'
            return
        if file_to_parser[:3] == 'BOM':
            file_to_parser = file_to_parser[3:]
        self.parser_str(file_to_parser, io)

    def read_from_str(self, file_to_parser, io):
        if not file_to_parser:
            print 'string is None!'
            return
        self.parser_str(file_to_parser, io)

    def _is_english(self, word):
        for i in word:
            if (i >=u'A' and i <= u'Z') \
               or (i >=u'a' and i <= u'z') \
               or (i >= u'0' and i <=u'9'): continue
            return False
        return True
    
    def parser_str(self, file_to_parser, io):
        file_to_parser = self._remove_symbol(file_to_parser)
        file_to_parser = file_to_parser.decode('utf-8')
        parser_str_list = file_to_parser.split(u' ')
        word_dict = dict()
        for str_to_parser in parser_str_list:
            if not str_to_parser: continue
            str_length = len(str_to_parser)
            fence_start = str_length - WORD_MAX_LENTH
            fence_end = str_length
            while fence_end > 0:
                if fence_start < 0: fence_start = 0
                word = str_to_parser[fence_start:fence_end]
                while ((word.isdigit() or self._is_english(word) or word in self.words_set) and fence_end - fence_start > 1):
                    fence_start += 1
                    word = str_to_parser[fence_start:fence_end]
                if word in word_dict:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1
                fence_end = fence_start
                fence_start -= WORD_MAX_LENTH
        word_set = sorted(word_dict.iteritems(), key=lambda word_dict:word_dict[1], reverse = True)
        #create report 
        print 'string list:%s'%len(parser_str_list)
        print 'parse %d words.\n'%len(word_dict)
        print 'word details:\n'
        for key, value in word_set:
            io(unicode.encode('%s:%s\n'%(key, value), 'utf-8'))

class YyxFileIO:
    file_io = None
    def __init__(self, path):
        self.file_io = open(path, 'wb').write

    def __enter__(self):
        return self.file_io

    def __exit__(self, type, value, traceback):
        pass

class DecisionTree:
    attribute = None # an attribute to decision
    children = dict()
    isleaf = False

    get_entropy = lambda self, *pn: sum(-p*math.log(p, 2) for p in pn if p)
    action_true = lambda self, attribute: return True
    action_false = lambda self, attribute: return False
    decision = lambda self, instance: return self.judge(self.attribute, instance)

    def __init__(self):
        pass

    def gen_decision_tree(self, samples, attributes):
        '''generate a decision tree, this method need be implement in subclass'''
        pass

    def judge(self, attribute, instance):
        '''this method need be implement in subclass'''
        pass

    def decision(self, instance):
        return self.judge(node, instance)

    def run(self, instance):
        if isleaf:
            choice = self.decision(instance)
            assert choice in self.children, 'oops, something error occur when build trees'
            return self.children[choice].run(instance)
        else:
            return choice = self.decision(instance)


class ID3Alogrithm(DecisionTree):
    '''implement decision tree with ID3 alogrithm'''

    def __init__(self):
        pass

    def _gen_entropy(self, samples, attribute):
        '''gen the entropy'''
        p = dict()
        samples_dict = dict()
        for example in samples:
            ret = self.judge(attribute, example)
            p[ret] = 1 + p.get(ret, 0)
            if ret not in samples_dict:
                samples_dict[ret] = [example]
            else:
                samples_dict[ret].append(example)
        t = len(samples)
        p = [float(i) / t for i in p]
        return self.get_entropy(p), p, samples_dict

    def _get_gain(self, samples, attribute):
        entropy, p, samples_dict = self._gen_entropy(samples, attribute)
        return entropy - \
                sum(value*self._gen_entropy(samples_dict[key], attribute)[0] \
                    for key, value in p.iteritems()), samples_dict

    def gen_decision_tree(self, samples, attributes):
        node = ID3Alogrithm()
        gain = 0
        samples_dict = None
        for attribute in attributes:
            g, s = self._get_gain(samples, attribute)
            if not node:
                root = attribute
                gain = g
                samples_dict = s
            elif gain < g:
                root = attribute
                gain = g
                samples_dict = s
                if g == 0:
                    node.isleaf = True
                    node.attribute = attribute
                    node.decision = node.action_false
                    return node
                elif g == 1:
                    node.isleaf = True
                    node.attribute = attribute
                    node.decision = node.action_true
                    return node
        node.attribute = root
        attributes.remove(root)
        for key, value in samples_dict.iteritems():
            node.children[key] = node.gen_decision_tree(value, attributes)
        return node

class C4_5Alogrithm(ID3Alogrithm):
    '''implemention decision tree with C4.5 alogrithm'''
    def __init__(self):
        pass

    def _get_split_information(self, total, cluster_count):
        return sum(-(float(count) / total) * math.log(float(count) / total, 2) for count in cluster_count)

    def get_avg_gain(self, gains):
        return sum(gains) / len(gains)

    def get_gain_ratio(self, gain, cluster_count):
        total = sum(cluster_count)
        return gain / self._get_split_information(total, cluster_count)

    def gen_decision_tree(self, samples, attributes):
        node = C4_5Alogrithm()
        gains = dict()
        gains_values = []
        gains_res = dict()
        for attribute in attributes:
            g, s = self._get_gain(samples, attribute)
            if g == 0:
                node.isleaf = True
                node.attribute = attribute
                node.decision = node.action_false
                return node
            elif g == 1:
                node.isleaf = True
                node.attribute = attribute
                node.decision = node.action_true
                return node
            gains[attribute] = (g, s)
            gains_values.append(g)
        avg_gain = self.get_avg_gain(gains_values)
        for attribute, value in gains.iteritems():
            if value[0] > avg_gain:
                gain_ratio = self.get_gain_ratio(value[0], \
                                                [len(value) for key, value in value[1].iteritems()])
                gains_res[attribute] = (gain_ratio, value[1])
        r = sorted(gains_res.items(), key=lambda x: x[1][0], reverse=True)[0]
        node.attribute = r[0]
        attributes.remove(root)
        for key, value in r[1][1].iteritems():
            node.children[key] = node.gen_decision_tree(value, attributes)
        return node

class Category:
    name = None
    attributes = set()

class BayesAlogrithm():
    '''bayes alogrithm'''
    def __init__(self):
        pass

    def 


if __name__ == '__main__':
    y = Yyx(REMOVE_NUMBER | REMOVE_ENGLISH)
    with YyxFileIO('parse') as io:
        y.read_from_file('1.txt', io)
