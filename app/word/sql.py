import json
import xml.etree.cElementTree as ET

import requests


class OperateDB(object):
    def __init__(self, conn):
        self.conn = conn
        self.table = ('word_mini', 'word_slim', 'word_entire')

    def select_list(self, word, **kwargs):
        word = word.replace('\'', '\'\'').replace('%', '%%')
        kwargs = kwargs['kwargs']
        if 'pron' in kwargs:
            kwargs['uk_pron'] = True
            kwargs['us_pron'] = True
        count = kwargs['count'] if 'count' in kwargs else 1
        fields_list = ['word', 'chn_def']
        optional_fields = {'uk_pron': 'uk_pron',
                           'us_pron': 'us_pron',
                           'eng': 'eng_def',
                           'tag': 'tag'}
        for field in optional_fields.keys():
            if field in kwargs and kwargs[field] == True:
                fields_list.append(optional_fields[field])
        fields = ', '.join(fields_list)

        data = []
        findlemma = False
        if count == 1:
            sql = ('SELECT * '
                   'FROM exchange '
                   'WHERE word=\'{word}\'').format(word=word)
            result = self.conn.execute(sql).fetchone()
            if result:
                findlemma = True
                word_in = word
                # word = result[2]
                exchange_str = self.get_exchange_str(result[3:])
            for t in self.table:
                list_sql = ('SELECT {fields} '
                            'FROM {table} '
                            'WHERE word=\'{word}\'').format(
                                fields=fields, table=t, word=word)
                result = self.conn.execute(list_sql).fetchone()
                if result:
                    data.append(result)
                    break
        else:
            for t in self.table:
                list_sql = ('SELECT {fields} '
                            'FROM {table} '
                            'WHERE word LIKE \'{word}%%\' AND is_lemma=1 '
                            'ORDER BY base '
                            'LIMIT {count}').format(
                                fields=fields, table=t, word=word, count=count)
                result = self.conn.execute(list_sql).fetchall()
                count -= len(result)
                data.extend(result)
                if count == 0:
                    break

        if len(data) == 0:
            return {'status': False}
        result = {'status': True, 'data': []}
        for item in data:
            item = list(item)
            d = {}
            if findlemma:
                d['word_in'] = word_in
                d['lemma'] = {'word': word, 'relation': exchange_str}
            for i in range(len(fields_list)):
                d['word_in'] = word
                if item[i]:
                    d[fields_list[i]] = item[i]
            result['data'].append(d)
        return result

    def select_detail(self, word):
        word = word.replace('\'', '\'\'').replace('%', '%%')
        fields_list = ['collins', 'bnc', 'frq', 'oxford_detail', 'cambridge_detail',
                       'longman_detail', 'collins_detail', 'net_detail', 'exchange']
        fields = ', '.join(fields_list)

        for t in self.table:
            detail_sql = ('SELECT {fields} '
                          'FROM {table} '
                          'WHERE word =\'{word}\'').format(fields=fields, table=t, word=word)
            result = self.conn.execute(detail_sql).fetchone()
            if result is not None:
                data = result
                break

        exchange = data[-1]
        derivative_dict = []
        if exchange and '0' not in exchange:
            dict_d = {}
            l = ['p', 'd', 'i', '3', 'r', 't', 's']
            derivative_dict = {}
            for derivatives in exchange.split('/'):
                form, derivative = derivatives.split(':')
                try:
                    dict_d[derivative] += form
                except KeyError:
                    dict_d[derivative] = form
            for derivative in dict_d:
                total_form = dict_d[derivative]
                derivative_dict[derivative] = self.get_exchange_str(
                    [form in total_form for form in l])

        if len(data) == 0:
            return {'status': False}
        d = {}
        if derivative_dict != []:
            d['derivative'] = derivative_dict
        for i in range(len(fields_list[:-1])):
            if data[i]:
                d[fields_list[i]] = data[i]
        result = {'status': True, 'data': d}
        return result

    def request_iciba(self, word):
        params = {'w': word, 'key': '341DEFE6E5CA504E62A567082590D0BD'}
        xml_bytes = requests.get(
            'http://dict-co.iciba.com/api/dictionary.php', params=params).content
        root = ET.fromstring(xml_bytes)
        sentence_list = []
        for sent in root.findall('sent'):
            eng, chn = sent.getchildren()
            eng = eng.text.strip()
            chn = chn.text.strip()
            sentence_list.append((eng, chn))
        sentence = ['\n'.join([eng.replace('\'', '\'\''),
                               chn.replace('\'', '\'\'')])
                    for eng, chn in sentence_list]
        sentence = '\r\n'.join(sentence)
        sql = ('UPDATE word_mini '
               'SET net_detail=\'{sentence}\' '
               'WHERE word=\'{word}\'').format(sentence=sentence, word=word)
        self.conn.execute(sql)
        sql = ('UPDATE word_slim '
               'SET net_detail=\'{sentence}\' '
               'WHERE word=\'{word}\'').format(sentence=sentence, word=word)
        self.conn.execute(sql)
        sql = ('UPDATE word_entire '
               'SET net_detail=\'{sentence}\' '
               'WHERE word=\'{word}\'').format(sentence=sentence, word=word)
        self.conn.execute(sql)
        return sentence_list

    def get_exchange_str(self, exchange_list):
        if not any(exchange_list):
            return ''
        l = ["过去式、", "过去分词、", "现在分词、", "第三人称单数、",
             "比较级、", "最高级、", "名词复数、"]
        return ''.join(list(map(lambda x, y: x if y else '', l, exchange_list)))[:-1]
