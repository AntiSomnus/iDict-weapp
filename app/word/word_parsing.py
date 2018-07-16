import re

from .. import conn
from .sql import SelectSQL, UpdateDetail
from .WordDetailProto_pb2 import (Explain, Relation, Sentence, WordDetail,
                                  WordList)

select_SQL = SelectSQL(conn)
update_detail = UpdateDetail(conn)

class GetWordList(object):
    def get_word_list(self, request_word, count, is_divide, is_tag_list):
        word_list = WordList()
        result_list = select_SQL.select(request_word, 'list', count)
        if result_list['status']:
            for result_item in result_list['data']:
                word_detail = WordDetail()
                word_detail.word = result_item['word']
                if is_tag_list:
                    word_detail.tag_flag.extend(self.get_tag_list(result_item['tag']))
                else:
                    word_detail.tag = result_item['tag']
                if is_divide:
                    explains_list = self.get_word_chn_explains_in_list(result_item['translation'])
                    for explain in explains_list:
                        word_detail.explain.extend([Explain(pos=explain[0], meaning=explain[1])])
                else:
                    word_detail.explain.extend([Explain(pos='', meaning=result_item['translation'])])
                word_list.wordDetail.extend([word_detail])
        return word_list

    def get_tag_list(self, tag_str):
        if not tag_str:
            return []
        tag_list = []
        tag_list.append(1 if 'zk' in tag_str else 0)
        tag_list.append(1 if 'gk' in tag_str else 0)
        tag_list.append(1 if 'ky' in tag_str else 0)
        tag_list.append(1 if 'cet4' in tag_str else 0)
        tag_list.append(1 if 'cet6' in tag_str else 0)
        tag_list.append(1 if 'toefl' in tag_str else 0)
        tag_list.append(1 if 'ielts' in tag_str else 0)
        tag_list.append(1 if 'gre' in tag_str else 0)
        return tag_list

    def get_word_chn_explains_in_list(self, word_chn_explains_in_line):
        l = []
        for explain in word_chn_explains_in_line.split("\n"):
            explain_pos_meaning = explain.split(' ', 1)
            if len(explain_pos_meaning) == 2:
                l.append(explain.split(' ', 1))
            else:
                l.append(['', explain])
        return l


class GetWordDetail(object):
    def __init__(self, request_word, is_stem):
        self.request_word = request_word
        self.actual_query_word = request_word

        self.word_detail = WordDetail()
        self.word_detail.word = request_word

        self.result = select_SQL.select(request_word, 'detail', 1)
        if self.result['status']:
            if is_stem:
                self.find_plain()
            if self.result['definition']:
                self.word_detail.eng_explain = self.result['definition']
            if self.result['collins']:
                self.word_detail.collins = self.result['collins']
            if self.result['tag']:
                self.word_detail.tag = self.result['tag']
            if self.result['detail']:
                sentence_list = self.result['detail'].split('\r\n')
                if sentence_list[-1] == '':
                    sentence_list = sentence_list[:-1]
                sentence_list = [Sentence(source='detail',
                                          eng=s.split('\n')[0],
                                          chn=s.split('\n')[1])
                                 for s in sentence_list]
                self.word_detail.sentence.extend(sentence_list)
            if self.result['oxford_detail']:
                sentence_list = self.result['oxford_detail'].split('\r\n')
                if sentence_list[-1] == '':
                    sentence_list = sentence_list[:-1]
                split_sentence_list = []
                for s in sentence_list:
                    s = s.split('\n')
                    if len(s) == 1:
                        s.append('')
                    split_sentence_list.append(s)
                sentence_list = [Sentence(source='oxford_detail',
                                          eng=s[0], chn=s[1])
                                 for s in split_sentence_list]
                self.word_detail.sentence.extend(sentence_list)
            if self.result['net_detail']:
                sentence_list = self.result['net_detail'].split('\r\n')
                if sentence_list[-1] == '':
                    sentence_list = sentence_list[:-1]
                sentence_list = [Sentence(source='net_detail',
                                          eng=s.split('\n')[0],
                                          chn=s.split('\n')[1])
                                 for s in sentence_list]
                self.word_detail.sentence.extend(sentence_list)
            else:
                sentence_list = update_detail.fetch_from_iciba(
                    self.actual_query_word)
                sentence_list = [Sentence(source='net_detail',
                                          eng=eng, chn=chn)
                                 for eng, chn in sentence_list]
                self.word_detail.sentence.extend(sentence_list)

    def find_plain(self):
        relation = Relation()
        exchange = self.result['exchange']
        match_0 = re.findall(r"0:[^/]+", exchange)
        match_1 = re.findall(r"1:[^/]+", exchange)

        if len(match_0) == 1 and len(match_1) == 1:
            relation.plain_word = match_0[0][2:]
            relation.relationship = match_1[0][2:]
            self.result = select_SQL.select(relation.plain_word)
        else:
            relation.plain_word = self.request_word
        self.word_detail.relation.CopyFrom(relation)
        self.actual_query_word = relation.plain_word
