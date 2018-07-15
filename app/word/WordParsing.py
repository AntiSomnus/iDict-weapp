import re
import xml.etree.cElementTree as ET

import requests

from .. import conn
from .select import SelectSQL
from .update_detail import UpdateDetail
from .WordDetailProto_pb2 import Relation, WordDetail

select_SQL = SelectSQL(conn)
update_detail = UpdateDetail(conn)


class WordProcess:
    def __init__(self, request_word, is_stem):
        self.request_word = request_word
        self.actual_query_word = request_word

        self.word_detail = WordDetail()
        self.word_detail.word = request_word

        result = select_SQL.select(request_word)
        if result['status']:
            self.offline_detail_dict = result

            if self.offline_detail_dict:
                if is_stem:
                    self.find_plain()
                self.word_detail.eng_explain = self.offline_detail_dict['definition']
                self.word_detail.collins = self.offline_detail_dict['collins']
                self.word_detail.tag = self.offline_detail_dict['tag']
            self.word_detail = update_detail.fetch_from_iciba(
                self.actual_query_word, self.word_detail)

    def find_plain(self):
        relation = Relation()
        exchange = self.offline_detail_dict['exchange']
        match_0 = re.findall(r"0:[^/]+", exchange)
        match_1 = re.findall(r"1:[^/]+", exchange)

        if len(match_0) == 1 and len(match_1) == 1:
            relation.plain_word = match_0[0][2:]
            relation.relationship = match_1[0][2:]
            self.offline_detail_dict = select_SQL.select(relation.plain_word)
        else:
            relation.plain_word = self.request_word
        self.word_detail.relation.CopyFrom(relation)
        self.actual_query_word = relation.plain_word
