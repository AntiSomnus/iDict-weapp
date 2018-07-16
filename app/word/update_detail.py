import xml.etree.cElementTree as ET

import requests

from .. import conn
from .WordDetailProto_pb2 import Sentence


class UpdateDetail(object):
    def __init__(self, conn):
        self.conn = conn

    def fetch_from_iciba(self, key):
        params = {'w': key, 'key': '341DEFE6E5CA504E62A567082590D0BD'}
        xml_bytes = requests.get(
            'http://dict-co.iciba.com/api/dictionary.php', params=params).content
        return self.parsing_from_xml(key, xml_bytes)

    def parsing_from_xml(self, key, xml_bytes):
        root = ET.fromstring(xml_bytes)
        sentence_list = []
        for sent in root.findall('sent'):
            eng, chn = sent.getchildren()
            eng = eng.text.strip()
            chn = chn.text.strip()
            sentence_list.append((eng, chn))
        sentence = ['\n'.join([eng.replace('\'', '\'\''),
                               chn.replace('\'', '\'\'')])
                    for eng, chn in sentence_list]
        sentence = '\r\n'.join(sentence)
        sql = ('UPDATE word_mini '
               'SET net_detail=\'{sentence}\' '
               'WHERE word=\'{key}\'').format(sentence=sentence, key=key)
        self.conn.execute(sql)
        sql = ('UPDATE word_slim '
               'SET net_detail=\'{sentence}\' '
               'WHERE word=\'{key}\'').format(sentence=sentence, key=key)
        self.conn.execute(sql)
        sql = ('UPDATE word_entire '
               'SET net_detail=\'{sentence}\' '
               'WHERE word=\'{key}\'').format(sentence=sentence, key=key)
        self.conn.execute(sql)
        return sentence_list
