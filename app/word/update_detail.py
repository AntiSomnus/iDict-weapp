import xml.etree.cElementTree as ET

import requests

from .. import conn
from .WordDetailProto_pb2 import Explain, Pron, Sentence


class UpdateDetail(object):
    def __init__(self, conn):
        self.conn = conn

    def fetch_from_iciba(self, key, word_detail):
        params = {'w': key, 'key': '341DEFE6E5CA504E62A567082590D0BD'}
        xml_bytes = requests.get(
            'http://dict-co.iciba.com/api/dictionary.php', params=params).content
        return self.parsing_from_xml(xml_bytes, word_detail)

    def parsing_from_xml(self, xml_bytes, word_detail):
        # get root
        root = ET.fromstring(xml_bytes)

        # get ps and url
        ps_list = root.findall('ps')
        pron_list = root.findall('pron')
        min_len = min(len(ps_list), len(pron_list))
        if min_len > 0:
            word_detail.pron_bri.CopyFrom(
                Pron(ps=ps_list[0].text, url=pron_list[0].text))
            if min_len > 1:
                word_detail.pron_ame.CopyFrom(
                    Pron(ps=ps_list[1].text, url=pron_list[1].text))

        # get pos and meaning
        pos_list = root.findall('pos')
        meaning_list = root.findall('acceptation')
        explain_list = []
        min_len = min(len(pos_list), len(meaning_list))
        for i in range(min_len):
            explain_list.append(
                Explain(pos=pos_list[i].text, meaning=meaning_list[i].text))
        word_detail.explain.extend(explain_list)

        # get sentence and translation
        sentence_list = []
        for sent in root.findall('sent'):
            eng, chn = sent.getchildren()
            sentence_list.append(
                Sentence(eng=eng.text.strip(), chn=chn.text.strip()))
        word_detail.sentence.extend(sentence_list)
        return word_detail
