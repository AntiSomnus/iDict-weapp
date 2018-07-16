# import re

from .sql import OperateDB
from . import WordProto_pb2 as wp

from .. import conn

sql = OperateDB(conn)


class GetWordList(object):
    def get_word_list(self, request_word, **kwargs):
        word_list = wp.WordList()
        result = sql.select_list(request_word, **kwargs)
        if result['status']:
            for data in result['data']:
                word_list.append(self.get_brief(data))
        return word_list

    def get_brief(self, data):
        word_brief = wp.WordBrief()
        word_brief.word_in = data['word']
        word_brief.word_out = data['word']

        word_lemma = wp.Lemma()
        if 'lemma' in data:
            word_lemma.isLemma = False
            word_lemma.relation = data['lemma']['relation']
            word_brief.word_out = data['lemma']['word']
        else:
            word_lemma.isLemma = True
        word_brief.Lemma.MergeFrom(word_lemma)

        # phonetic
        # word_pron = wp.Pronunciation()
        # if 'pron' in self.data:
        # pass

        if 'eng_def' in data:
            eng_defs = data['eng_def']
            for eng_def in eng_defs.split("\n"):
                word_eng_def = wp.Definition()
                pos_meaning = eng_def.split(' ', 1)
                if len(pos_meaning) == 2:
                    word_eng_def.pos = pos_meaning[0]
                    word_eng_def.meaning = pos_meaning[1]
                else:
                    word_eng_def.meaning = eng_def
                word_brief.eng_definitions.append(word_eng_def)
        if 'chn_def' in data:
            chn_defs = data['chn_def']
            for chn_def in chn_defs.split("\n"):
                word_chn_def = wp.Definition()
                pos_meaning = chn_def.split(' ', 1)
                if len(pos_meaning) == 2:
                    word_chn_def.pos = pos_meaning[0]
                    word_chn_def.meaning = pos_meaning[1]
                else:
                    word_chn_def.meaning = chn_def
                word_brief.chn_definitions.append(word_chn_def)

        if 'tag' in data:
            tag_str = data['tag']
            tag_list = []
            tag_list.append(1 if 'zk' in tag_str else 0)
            tag_list.append(1 if 'gk' in tag_str else 0)
            tag_list.append(1 if 'ky' in tag_str else 0)
            tag_list.append(1 if 'cet4' in tag_str else 0)
            tag_list.append(1 if 'cet6' in tag_str else 0)
            tag_list.append(1 if 'toefl' in tag_str else 0)
            tag_list.append(1 if 'ielts' in tag_str else 0)
            tag_list.append(1 if 'gre' in tag_str else 0)
            word_brief.tags = tag_list

        return word_brief


class GetWordDetail(GetWordList):
    def get_word_detail(self, request_word, **kwargs):
        word_brief = self.get_word_list(request_word, **kwargs)
        word_detail = WordDetail()
        word_detail.word_brief = word_brief
        request_word = word_brief.word_out
        result = sql.select_detail(request_word)
        if result['status']:
            data = result['data']

            if 'collins' in data:
                word_detail.collins = data['collins']

            if 'bnc' in data:
                word_detail.bnc = data['bnc']

            if 'frq' in data:
                word_detail.frq = data['frq']

            if 'oxford_detail' in data:
                sentence_list = data['oxford_detail'].split('\r\n')
                if sentence_list[-1] == '':
                    sentence_list = sentence_list[:-1]
                split_sentence_list = []
                for s in sentence_list:
                    s = s.split('\n')
                    if len(s) == 1:
                        s.append('')
                    split_sentence_list.append(s)
                sentence_list = [wp.Sentence(source=1, eng=s[0], chn=s[1])
                                 for s in split_sentence_list]
                word_detail.sentences.extend(sentence_list)

            if 'net_detail' in data:
                sentence_list = data['net_detail'].split('\r\n')
                if sentence_list[-1] == '':
                    sentence_list = sentence_list[:-1]
                split_sentence_list = []
                for s in sentence_list:
                    s = s.split('\n')
                    if len(s) == 1:
                        s.append('')
                    split_sentence_list.append(s)
                sentence_list = [wp.Sentence(source=0, eng=s[0], chn=s[1])
                                 for s in sentence_list]
                word_detail.sentence.extend(sentence_list)
            # iciba
            # else:
            #     sentence_list = sql.update_detail(request_word)
            #     sentence_list = [wp.Sentence(source=0, eng=eng, chn=chn)
            #                      for eng, chn in sentence_list]
            #     word_detail.sentence.extend(sentence_list)

            if 'derivative' in data:
                for item in data['derivative']:
                    d = wp.Derivative(item[0], item[1])
                    word_detail.derivatives.append(d)

        return word_detail
