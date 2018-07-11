import re
import xml.etree.cElementTree as ET

import requests

from Dict.stardict import DictCsv
from WordDetailProto_pb2 import WordDetail, Pron, Explain, Sentence, Relation

offline_dict = DictCsv("static/ecdict.csv")
print("init_finish")


class WordProcess:
    def __init__(self, request_word, is_stem):
        self.request_word = request_word
        self.actual_query_word = request_word

        self.word_detail = WordDetail()
        self.word_detail.word = request_word

        self.offline_detail_dict = offline_dict.query(request_word)

        if self.offline_detail_dict:
            if is_stem:
                self.find_plain()
            self.word_detail.eng_explain = self.offline_detail_dict['definition']
            self.word_detail.collins = self.offline_detail_dict['collins']
            self.word_detail.tag = self.offline_detail_dict['tag']
        self.fetch_from_iciba()

    def find_plain(self):
        relation = Relation()
        exchange = self.offline_detail_dict['exchange']
        match_0 = re.findall(r"0:[^/]+", exchange)
        match_1 = re.findall(r"1:[^/]+", exchange)

        if len(match_0) == 1 and len(match_1) == 1:
            relation.plain_word = match_0[0][2:]
            relation.relationship = match_1[0][2:]
            self.offline_detail_dict = offline_dict.query(relation.plain_word)
        else:
            relation.plain_word = self.request_word
        self.word_detail.relation.CopyFrom(relation)
        self.actual_query_word = relation.plain_word

    def fetch_from_iciba(self):
        params = {'w': self.actual_query_word, 'key': '341DEFE6E5CA504E62A567082590D0BD'}
        xml_bytes = requests.get('http://dict-co.iciba.com/api/dictionary.php', params=params).content
        self.parsing_from_xml(xml_bytes)

    def parsing_from_xml(self, xml_bytes):
        # get root
        root = ET.fromstring(xml_bytes)

        # get ps and url
        ps_list = root.findall('ps')
        pron_list = root.findall('pron')
        min_len = min(len(ps_list), len(pron_list))
        if min_len > 0:
            self.word_detail.pron_bri.CopyFrom(Pron(ps=ps_list[0].text, url=pron_list[0].text))
            if min_len > 1:
                self.word_detail.pron_ame.CopyFrom(Pron(ps=ps_list[1].text, url=pron_list[1].text))

        # get pos and meaning
        pos_list = root.findall('pos')
        meaning_list = root.findall('acceptation')
        explain_list = []
        min_len = min(len(pos_list), len(meaning_list))
        for i in range(min_len):
            explain_list.append(Explain(pos=pos_list[i].text, meaning=meaning_list[i].text))
        self.word_detail.explain.extend(explain_list)

        # get sentence and translation
        sentence_list = []
        for sent in root.findall('sent'):
            eng, chn = sent.getchildren()
            sentence_list.append(Sentence(eng=eng.text.strip(), chn=chn.text.strip()))
        self.word_detail.sentence.extend(sentence_list)
