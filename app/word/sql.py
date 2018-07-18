import json
import xml.etree.cElementTree as ET

import requests

class OperateDB(object):
    def __init__(self, conn):
        self.conn = conn
        self.table = ('word_mini', 'word_slim', 'word_entire')

    def select_list(self, word, **kwargs):
        word = word.replace('\'', '\'\'').replace('%','%%')
        kwargs = kwargs['kwargs']
        count = kwargs['count'] if 'count' in kwargs else 1
        fields = ['word', 'chn_def']
        optional_fields = {'pron': 'uk_pron, us_pron',
                           'eng': 'eng_def',
                           'tag': 'tag'}
        for field in optional_fields.keys():
            if field in kwargs and kwargs[field] == True:
                fields.append(optional_fields[field])
        fields = ', '.join(fields)

        findlemma = False
        if count == 1:
            sql = ('SELECT * '
                   'FROM exchange '
                   'WHERE word=\'{word}\' ').format(word=word)
            result = self.conn.execute(sql).fetchone()
            if result:
                findlemma = True
                word = result[2]
                exchange_str = self.get_exchange_str(result[3:])

        data = []
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
            d = {}
            if findlemma:
                d['lemma'] = {'word': word, 'relation': exchange_str}
            d['word'] = item[0]
            d['chn_def'] = item[1] if item[1] else ''
            if item[2]:
                d['uk_pron'] = item[2]
            if item[3]:
                d['us_pron'] = item[3]
            if item[4]:
                d['eng_def'] = item[4]
            if item[5]:
                d['tag'] = item[5]
            result['data'].append(d)
        return result

    def get_exchange_str(self, exchange_list):
        if not any(exchange_list):
            return ''
        l = ["过去式、", "过去分词、", "现在分词、", "第三人称单数、", "比较级、", "最高级、", "名词复数、"]
        return ''.join(list(map(lambda x, y: x if y else '', l, exchange_list)))[:-1]

    def get_list_data(self, sql, count):
        result = self.conn.execute(sql).fetchall()
        if result != []:
            count -= len(result)
        return result, count

    def select_detail(self, word):
        word = word.replace('\'', '\'\'').replace('%','%%')
        fields = ['collins', 'bnc', 'frq', 'oxford_detail', 'collins_detail', 'net_detail', 'exchange']
        fields = ', '.join(fields)

        for t in self.table:
            detail_sql = ('SELECT {fields} '
                          'FROM {table} '
                          'WHERE word =\'{word}\'').format(fields=fields, table=t, word=word)
            result = self.conn.execute(detail_sql).fetchone()
            if result is not None:
                data = result
                break

        exchange = data[-1]
        if '0' in exchange:
            return []
        else:
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
                derivative_dict[derivative] = self.get_exchange_str([form in total_form for form in l])

        if len(data) == 0:
            return {'status': False}
        d= {}
        if data[0]:
            d['collins'] = data[0]
        if data[1]:
            d['bnc'] = data[1]
        if data[2]:
            d['frq'] = data[2]
        if data[3]:
            d['oxford_detail'] = data[3]
        if data[4]:
            d['collins_detail'] = data[4]
        if data[5]:
            d['net_detail'] = data[5]
        d['derivative'] = derivative_dict
        result = {'status': True, 'data': d}
        return result

    def request_iciba(self, word):
        params = {'w': word, 'key': '341DEFE6E5CA504E62A567082590D0BD'}
        xml_bytes = requests.get(
            'http://dict-co.iciba.com/api/dictionary.php', params=params).content
        return self.parsing_from_xml(word, xml_bytes)

    def parsing_from_xml(self, word, xml_bytes):
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
