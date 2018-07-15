import re
import xml.etree.cElementTree as ET

import requests

from .. import conn
from .select_word import SelectSQL
from .update_detail import UpdateDetail
from .WordDetailProto_pb2 import Relation, Sentence, WordDetail

select_SQL = SelectSQL(conn)
update_detail = UpdateDetail(conn)


class WordProcess:
    def __init__(self, request_word, is_stem):
        self.request_word = request_word
        self.actual_query_word = request_word

        self.word_detail = WordDetail()
        self.word_detail.word = request_word

        self.result = select_SQL.select(request_word)
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
                sentence_list = [Sentence(source='oxford_detail',
                                          eng=s.split('\n')[0],
                                          chn=s.split('\n')[1])
                                 for s in sentence_list]
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
