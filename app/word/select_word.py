import json


class SelectSQL(object):
    def __init__(self, conn):
        self.conn = conn
        self.mode = ''
        self.count = 1
        self.fields = ('id', 'word', 'sw', 'phonetic', 'definition',
                       'translation', 'pos', 'collins', 'oxford', 'tag',
                       'bnc', 'frq', 'base', 'exchange', 'detail',
                       'oxford_detail', 'net_detail', 'audio')
        self.list_sql = ('SELECT word, translation, tag '
                         'FROM {table} '
                         'WHERE word LIKE \'{key}%%\' '
                         'ORDER BY base '
                         'LIMIT {count}')
        self.detail_sql = ('SELECT * '
                           'FROM {table} '
                           'WHERE word=\'{key}\' ')

    def select(self, key, mode, count=1):
        if mode not in ('list', 'detail'):
            return {'status': False}
        self.mode = mode
        self.count = count
        result = self.select_mini(key)
        if result['status']:
            return self.tuple2dict(result['data'])
        result = self.select_slim(key)
        if result['status']:
            return self.tuple2dict(result['data'])
        result = self.select_entire(key)
        if result['status']:
            return self.tuple2dict(result['data'])
        return {'status': False}

    def select_mini(self, key):
        if self.mode == 'list':
            sql = self.list_sql.format(table='word_mini', key=key, count=self.count)
        if self.mode == 'detail':
            sql = self.detail_sql.format(table='word_mini', key=key)
        data = self.conn.execute(sql).fetchall()
        if data is None:
            return {'status': False}
        else:
            return {'status': True, 'data': data}

    def select_slim(self, key):
        if self.mode == 'list':
            sql = self.list_sql.format(table='word_slim', key=key, count=self.count)
        if self.mode == 'detail':
            sql = self.detail_sql.format(table='word_slim', key=key)
        data = self.conn.execute(sql).fetchall()
        if data is None:
            return {'status': False}
        else:
            return {'status': True, 'data': data}

    def select_entire(self, key):
        if self.mode == 'list':
            sql = self.list_sql.format(table='word_entire', key=key, count=self.count)
        if self.mode == 'detail':
            sql = self.detail_sql.format(table='word_entire', key=key)
        data = self.conn.execute(sql).fetchall()
        if data is None:
            return {'status': False}
        else:
            return {'status': True, 'data': data}

    def tuple2dict(self, data):
        if self.mode == 'list':
            words = {'status': True, 'data': []}
            data = [item for item in data]
            for item in data:
                d = {'word': item[0],
                     'translation': item[1].replace('\\n', '\n'),
                     'tag': item[2]}
                words['data'].append(d)
            return words
        if self.mode == 'detail':
            word = {'status': True}
            data = [item for item in data]
            for i in range(len(self.fields)):
                field = self.fields[i]
                if field in ('definition', 'translation'):
                    data[i] = data[i].replace('\\n', '\n')
                word[field] = data[i]
            if word['detail']:
                text = word['detail']
                try:
                    obj = json.loads(text)
                except:
                    obj = None
                word['detail'] = obj
            return word
