import json
# import xml.etree.cElementTree as ET

# import requests

class OperateDB(object):
    def __init__(self, conn):
        self.conn = conn
        self.table = ('word_mini', 'word_slim', 'word_entire')


    def select_list(self, word, **kwargs):
        word = word.replace('\'', '\'\'').replace('%','%%')
        if 'count' in kwargs:
            count = kwargs['count']
        else:
            count = 10
        fields = ['word', 'chn_def']
        optional_fields = {'pron': 'uk_pron, us_pron',
                           'eng': 'eng_def',
                           'tag': 'tag'}
        for field in optional_fields.keys():
            if field in kwargs and kwargs[field] == True:
                fields.append(optional_fields[field])
        fields = ' '.join(fields)

        list_sql = ('SELECT {fields} '
                    'FROM {table} '
                    'WHERE word LIKE \'{word}%%\' '
                    'ORDER BY base '
                    'LIMIT {count}').format(fields=fields, word=word)
        data = self.get_list_data(list_sql, count)

        if len(data) == 0:
            return {'status': False}
        result = {'status': True, 'data': []}
        for item in data:
            d = {}
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

    def get_list_data(self, list_sql, count):
        data = []
        for t in self.table:
            sql = list_sql.format(table=t, count=count)
            result = self.conn.execute(sql).fetchall()
            if result != []:
                data.extend(result)
                count -= len(data)
            if count == 0:
                break
        return data

    def select_detail(self, word):
        word = word.replace('\'', '\'\'').replace('%','%%')
        fields = ['collins', 'bnc', 'frq', 'oxford_detail', 'net_detail']
        fields = ' '.join(fields)

        detail_sql = ('SELECT {fields} '
                      'FROM {table} '
                      'WHERE word =\'{word}%%\'').format(fields=fields, word=word)
        data = self.get_detail_data(detail_sql)
        lemma = self.find_lemma(word)

        if len(data) == 0:
            return {'status': False}
        d = {'lemma': lemma}
        d['collins'] = data[0]
        d['bnc'] = data[1]
        d['frq'] = data[2]
        d['oxford_detail'] = data[3]
        d['net_detail'] = data[4]
        result = {'status': True, 'data': d}
        return result

    def get_detail_data(self, detail_sql):
        for t in self.table:
            sql = detail_sql.format(table=t)
            result = self.conn.execute(sql).fetchone()
            if result is not None:
                data = result
                break
        return data

    def find_lemma(self, word):
        sql = ('SELECT lemma, type '
               'FROM word_lemma '
               'WHERE word={word}').format(word=word)
        data = self.conn.execute(sql).fetchone()
        if data is not None:
            lemma = {'word': data[0], 'relation':data[1]}
        return lemma

# class UpdateDetail(object):
#     def __init__(self, conn):
#         self.conn = conn
#         self.key = ''

#     def fetch_from_iciba(self, key):
#         self.key = key
#         params = {'w': self.key, 'key': '341DEFE6E5CA504E62A567082590D0BD'}
#         xml_bytes = requests.get(
#             'http://dict-co.iciba.com/api/dictionary.php', params=params).content
#         return self.parsing_from_xml(xml_bytes)

#     def parsing_from_xml(self, xml_bytes):
#         root = ET.fromstring(xml_bytes)
#         sentence_list = []
#         for sent in root.findall('sent'):
#             eng, chn = sent.getchildren()
#             eng = eng.text.strip()
#             chn = chn.text.strip()
#             sentence_list.append((eng, chn))
#         sentence = ['\n'.join([eng.replace('\'', '\'\''),
#                                chn.replace('\'', '\'\'')])
#                     for eng, chn in sentence_list]
#         sentence = '\r\n'.join(sentence)
#         sql = ('UPDATE word_mini '
#                'SET net_detail=\'{sentence}\' '
#                'WHERE word=\'{key}\'').format(sentence=sentence, key=self.key)
#         self.conn.execute(sql)
#         sql = ('UPDATE word_slim '
#                'SET net_detail=\'{sentence}\' '
#                'WHERE word=\'{key}\'').format(sentence=sentence, key=self.key)
#         self.conn.execute(sql)
#         sql = ('UPDATE word_entire '
#                'SET net_detail=\'{sentence}\' '
#                'WHERE word=\'{key}\'').format(sentence=sentence, key=self.key)
#         self.conn.execute(sql)
#         return sentence_list
