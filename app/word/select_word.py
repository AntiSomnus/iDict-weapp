import json


class SelectSQL(object):
    def __init__(self, conn):
        self.conn = conn
        self.key = ''
        self.mode = ''
        self.count = 0
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

    def select(self, key, mode, count):
        if mode not in ('list', 'detail'):
            return {'status': False}
        # self.key = key.replace('\'', '\'\'').replace('%','%%')
        self.key = key
        self.mode = mode
        self.count = count
        result = self.select_mini()
        if result['status']:
            return self.tuple2dict(result['data'])
        result = self.select_slim()
        if result['status']:
            return self.tuple2dict(result['data'])
        result = self.select_entire()
        if result['status']:
            return self.tuple2dict(result['data'])
        return {'status': False}

    def select_mini(self):
        if self.mode == 'list':
            sql = self.list_sql.format(table='word_mini', key=self.key, count=self.count)
            data = self.conn.execute(sql).fetchall()
        if self.mode == 'detail':
            sql = self.detail_sql.format(table='word_mini', key=self.key)
            data = self.conn.execute(sql).fetchone()
        if data is None:
            return {'status': False}
        else:
            return {'status': True, 'data': data}

    def select_slim(self):
        if self.mode == 'list':
            sql = self.list_sql.format(table='word_slim', key=self.key, count=self.count)
            data = self.conn.execute(sql).fetchall()
        if self.mode == 'detail':
            sql = self.detail_sql.format(table='word_slim', key=self.key)
            data = self.conn.execute(sql).fetchone()
        if data is None:
            return {'status': False}
        else:
            return {'status': True, 'data': data}

    def select_entire(self):
        if self.mode == 'list':
            sql = self.list_sql.format(table='word_entire', key=self.key, count=self.count)
            data = self.conn.execute(sql).fetchall()
        if self.mode == 'detail':
            sql = self.detail_sql.format(table='word_entire', key=self.key)
            data = self.conn.execute(sql).fetchone()
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
