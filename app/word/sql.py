import json
import xml.etree.cElementTree as ET

import requests


class SelectSQL(object):
    def __init__(self, conn):
        self.conn = conn
        self.key = ''
        self.mode = ''
        self.count = 1
        self.fields = ('id', 'word', 'sw', 'phonetic', 'definition',
                       'translation', 'pos', 'collins', 'oxford', 'tag',
                       'bnc', 'frq', 'base', 'exchange', 'oxford_detail',
                       'net_detail', 'audio')
        self.list_sql = ('SELECT word, translation, tag '
                         'FROM {table} '
                         'WHERE word LIKE \'{key}%%\' '
                         'ORDER BY base '
                         'LIMIT {count}')
        self.detail_sql = ('SELECT * '
                           'FROM {table} '
                           'WHERE word=\'{key}\' ')

    def select(self, key, **kwargs):
        if 'mode' not in kwargs:
            return {'status': False}
        self.key = key.replace('\'', '\'\'').replace('%','%%')
        self.mode = kwargs['mode']
        if self.mode == 'list':
            self.count = kwargs['count']

        data = []
        result = self.select_mini()
        if result['status']:
            data.extend(result['data'])
            if self.count == 0:
                return self.tuple2dict(data)
        result = self.select_slim()
        if result['status']:
            data.extend(result['data'])
            if self.count == 0:
                return self.tuple2dict(data)
        result = self.select_entire()
        if result['status']:
            data.extend(result['data'])
            if self.count == 0:
                return self.tuple2dict(data)
        if len(data) > 0:
            return self.tuple2dict(data)
        return {'status': False}

    def select_mini(self):
        if self.mode == 'list':
            sql = self.list_sql.format(
                table='word_mini', key=self.key, count=self.count)
            data = self.conn.execute(sql).fetchall()
        if self.mode == 'detail':
            sql = self.detail_sql.format(
                table='word_mini', key=self.key)
            data = self.conn.execute(sql).fetchall()
        if data == []:
            return {'status': False}
        else:
            self.count -= len(data)
            return {'status': True, 'data': data}

    def select_slim(self):
        if self.mode == 'list':
            sql = self.list_sql.format(
                table='word_slim', key=self.key, count=self.count)
            data = self.conn.execute(sql).fetchall()
        if self.mode == 'detail':
            sql = self.detail_sql.format(
                table='word_slim', key=self.key)
            data = self.conn.execute(sql).fetchall()
        if data == []:
            return {'status': False}
        else:
            self.count -= len(data)
            return {'status': True, 'data': data}

    def select_entire(self):
        if self.mode == 'list':
            sql = self.list_sql.format(
                table='word_entire', key=self.key, count=self.count)
            data = self.conn.execute(sql).fetchall()
        if self.mode == 'detail':
            sql = self.detail_sql.format(
                table='word_entire', key=self.key)
            data = self.conn.execute(sql).fetchall()
        if data == []:
            return {'status': False}
        else:
            return {'status': True, 'data': data}

    def tuple2dict(self, data):
        if self.mode == 'list':
            words = {'status': True, 'data': []}
            data = [item for item in data]
            for item in data:
                if item[1]:
                    d = {'word': item[0],
                         'translation': item[1],
                         'tag': item[2]}
                else:
                    d = {'word': item[0],
                         'translation': '',
                         'tag': item[2]}
                words['data'].append(d)
            return words
        if self.mode == 'detail':
            word = {'status': True}
            print(data)
            data = [item for item in data[0]]
            for i in range(len(self.fields)):
                field = self.fields[i]
                if field in ('definition', 'translation'):
                    if data[i]:
                        data[i] = data[i].replace('\\n', '\n')
                word[field] = data[i]
            return word


class UpdateDetail(object):
    def __init__(self, conn):
        self.conn = conn
        self.key = ''

    def fetch_from_iciba(self, key):
        self.key = key
        params = {'w': self.key, 'key': '341DEFE6E5CA504E62A567082590D0BD'}
        xml_bytes = requests.get(
            'http://dict-co.iciba.com/api/dictionary.php', params=params).content
        return self.parsing_from_xml(xml_bytes)

    def parsing_from_xml(self, xml_bytes):
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
               'WHERE word=\'{key}\'').format(sentence=sentence, key=self.key)
        self.conn.execute(sql)
        sql = ('UPDATE word_slim '
               'SET net_detail=\'{sentence}\' '
               'WHERE word=\'{key}\'').format(sentence=sentence, key=self.key)
        self.conn.execute(sql)
        sql = ('UPDATE word_entire '
               'SET net_detail=\'{sentence}\' '
               'WHERE word=\'{key}\'').format(sentence=sentence, key=self.key)
        self.conn.execute(sql)
        return sentence_list
