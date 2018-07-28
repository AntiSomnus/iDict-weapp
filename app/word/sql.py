class OperateDB(object):
    def __init__(self, conn):
        self.conn = conn
        self.table = ('word_mini', 'word_slim', 'word_entire')
        sql = ('SELECT word, base FROM word_mini')
        data = self.conn.execute(sql).fetchall()
        self.spelling = {item[0]: item[1] for item in data}

    # corrector
    def correction(self, word):
        candidates = self.candidates(word)
        if candidates:
            return candidates[0]
        else:
            return word

    def candidates(self, word):
        candidates = {**self.known([word]),
                      **self.known(self.edits1(word)),
                      **self.known(self.edits2(word))}
        return sorted(candidates, key=candidates.get, reverse=False)

    def known(self, words):
        return {w: self.spelling[w] for w in words if w in self.spelling.keys()}

    def edits1(self, word):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    # brief
    def select_brief(self, word, **kwargs):
        word = word.replace('\'', '\'\'').replace('%', '%%')
        kwargs = kwargs['kwargs']
        if kwargs['pron'] == True:
            kwargs['uk_pron'] = True
            kwargs['us_pron'] = True
        fields_list = ['word', 'chn_def']
        optional_fields = {'uk_pron': 'uk_pron',
                           'us_pron': 'us_pron',
                           'eng': 'eng_def',
                           'tag': 'tag'}
        for field in optional_fields.keys():
            if field in kwargs and kwargs[field] == True:
                fields_list.append(optional_fields[field])
        fields = ', '.join(fields_list)

        result = {'status': False}
        data = []
        findlemma = False
        sql = ('SELECT * '
               'FROM exchange '
               'WHERE word=\'{word}\'').format(word=word)
        data = self.conn.execute(sql).fetchone()
        if data:
            findlemma = True
            word_in = word
            word = data[2]
            exchange_str = self.get_exchange_str(data[3:])
        for t in self.table:
            list_sql = ('SELECT {fields} '
                        'FROM {table} '
                        'WHERE word=\'{word}\'').format(
                            fields=fields, table=t, word=word)
            data = self.conn.execute(list_sql).fetchone()
            if data:
                data = list(data)
                break
        else:
            return result

        result['status'] = True
        d = {}
        for i in range(len(fields_list)):
            d['word_in'] = word
            if data[i]:
                d[fields_list[i]] = data[i]
        if findlemma:
            d['word_in'] = word_in
            d['lemma'] = {'word': word, 'relation': exchange_str}
        result['data'] = d
        return result

    # list
    def select_list(self, word, **kwargs):
        word = word.replace('\'', '\'\'').replace('%', '%%')
        kwargs = kwargs['kwargs']
        if kwargs['pron'] == True:
            kwargs['uk_pron'] = True
            kwargs['us_pron'] = True
        count = kwargs['count']
        fields_list = ['word', 'chn_def']
        optional_fields = {'uk_pron': 'uk_pron',
                           'us_pron': 'us_pron',
                           'eng': 'eng_def',
                           'tag': 'tag'}
        for field in optional_fields.keys():
            if field in kwargs and kwargs[field] == True:
                fields_list.append(optional_fields[field])
        fields = ', '.join(fields_list)

        result = {'status': False}
        data = []
        for t in self.table:
            sql = ('SELECT {fields} '
                   'FROM {table} '
                   'WHERE word=\'{word}\' ').format(
                       fields=fields, table=t, word=word)
            temp_data = self.conn.execute(sql).fetchone()
            if temp_data:
                data.append(temp_data)
                count -= 1
                break

        for t in self.table:
            sql = ('SELECT {fields} '
                   'FROM {table} '
                   'WHERE word LIKE \'{word}%%\' AND word!=\'{word}\' '
                   'ORDER BY base '
                   'LIMIT {count}').format(
                       fields=fields, table=t, word=word, count=count)
            temp_data = self.conn.execute(sql).fetchall()
            count -= len(temp_data)
            data.extend(temp_data)
            if count == 0:
                break
        else:
            if len(data) == 0:
                return result

        result['status'] = True
        result['data'] = []
        for item in data:
            item = list(item)
            d = {}
            for i in range(len(fields_list)):
                d['word_in'] = word
                if item[i]:
                    d[fields_list[i]] = item[i]
            result['data'].append(d)
        return result

    # detail
    def select_detail(self, word):
        word = word.replace('\'', '\'\'').replace('%', '%%')
        brief_fields = ['word', 'chn_def', 'uk_pron',
                        'us_pron', 'eng_def', 'tag']
        fields = ', '.join(brief_fields)

        result = {'status': False}
        brief_data = []
        findlemma = False
        sql = ('SELECT * '
               'FROM exchange '
               'WHERE word=\'{word}\'').format(word=word)
        data = self.conn.execute(sql).fetchone()
        if data:
            findlemma = True
            word_in = word
            word_out = data[2]
            exchange_str = self.get_exchange_str(data[3:])
        for t in self.table:
            sql = ('SELECT {fields} '
                   'FROM {table} '
                   'WHERE word=\'{word}\'').format(
                       fields=fields, table=t, word=word)
            data = self.conn.execute(sql).fetchone()
            if data:
                brief_data = list(data)
                break
        if len(brief_data) != 0:
            result['status'] = True
            d = {}
            for i in range(len(brief_fields)):
                d['word_in'] = word
                if brief_data[i]:
                    d[brief_fields[i]] = brief_data[i]
            if findlemma:
                d['word_in'] = word_in
                d['lemma'] = {'word': word_out, 'relation': exchange_str}
            result['brief'] = d

        detail_fields = ['collins', 'bnc', 'frq', 'oxford_detail',
                         'cambridge_detail', 'longman_detail',
                         'collins_detail', 'net_detail', 'exchange']
        fields = ', '.join(detail_fields)

        for t in self.table:
            detail_sql = ('SELECT {fields} '
                          'FROM {table} '
                          'WHERE word =\'{word}\'').format(
                              fields=fields, table=t, word=word)
            data = self.conn.execute(detail_sql).fetchone()
            if data is not None:
                break
        else:
            return result

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

        d = {}
        if derivative_dict != []:
            d['derivative'] = derivative_dict
        for i in range(len(detail_fields[:-1])):
            if data[i]:
                d[detail_fields[i]] = data[i]
        result['data'] = d
        return result

    def get_exchange_str(self, exchange_list):
        if not any(exchange_list):
            return ''
        l = ["过去式、", "过去分词、", "现在分词、", "第三人称单数、",
             "比较级、", "最高级、", "名词复数、"]
        return ''.join(
            list(map(lambda x, y: x if y else '', l, exchange_list)))[:-1]
