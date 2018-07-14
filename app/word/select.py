import json


class SelectSQL(object):
    def __init__(self, conn):
        self.conn = conn
        self.fields = ('id', 'word', 'sw', 'phonetic', 'definition',
                       'translation', 'pos', 'collins', 'oxford', 'tag',
                       'bnc', 'frq', 'exchange', 'detail', 'audio')

    def select(self, key):
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
        sql = ('SELECT * '
               'FROM mini '
               'WHERE word=\'{key}\'').format(key=key)
        data = self.conn.execute(sql).fetchone()
        if data is None:
            return {'status': False}
        else:
            times = data[-1] + 1
            sql = ('UPDATE mini '
                   'SET frequency={times} '
                   'WHERE word=\'{key}\'').format(times=times, key=key)
            self.conn.execute(sql)
            return {'status': True, 'data': data}

    def select_slim(self, key):
        sql = ('SELECT * '
               'FROM slim '
               'WHERE word=\'{key}\'').format(key=key)
        data = self.conn.execute(sql).fetchone()
        if data is None:
            return {'status': False}
        else:
            times = data[-1] + 1
            sql = ('UPDATE slim '
                   'SET frequency={times} '
                   'WHERE word=\'{key}\'').format(times=times, key=key)
            self.conn.execute(sql)
            return {'status': True, 'data': data}

    def select_entire(self, key):
        sql = ('SELECT * '
               'FROM entire '
               'WHERE word=\'{key}\'').format(key=key)
        data = self.conn.execute(sql).fetchone()
        if data is None:
            return {'status': False}
        else:
            times = data[-1] + 1
            sql = ('UPDATE entire '
                   'SET frequency={times} '
                   'WHERE word=\'{key}\'').format(times=times, key=key)
            self.conn.execute(sql)
            return {'status': True, 'data': data}

    def tuple2dict(self, data):
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
