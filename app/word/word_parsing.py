import re

from .sql import OperateDB
from . import WordProto_pb2 as wp

from .. import conn

sql = OperateDB(conn)


class GetWordList(object):
    def get_list(self, request_word, **kwargs):
        word_list = wp.WordList()
        result = sql.select_list(request_word, **kwargs)
        if result['status']:
            for data in result['data']:
                word_list.word_briefs.extend([self.get_brief(data)])
        return word_list

    def get_brief(self, data):
        word_brief = wp.WordBrief()
        word_brief.word_in = data['word']
        word_brief.word_out = data['word']

        word_lemma = wp.WordBrief.Lemma()
        if 'lemma' in data:
            word_lemma.isLemma = False
            word_lemma.relation = data['lemma']['relation']
            word_brief.word_out = data['lemma']['word']
        else:
            word_lemma.isLemma = True
        word_brief.lemma.MergeFrom(word_lemma)

        if 'uk_pron' in data:
            uk_pron = wp.WordBrief.Pronunciation()
            uk_pron.ps = data['uk_pron']
            word_brief.uk_pron.MergeFrom(uk_pron)
        if 'us_pron' in data:
            us_pron = wp.WordBrief.Pronunciation()
            us_pron.ps = data['us_pron']
            word_brief.us_pron.MergeFrom(us_pron)

        if 'eng_def' in data:
            eng_defs = data['eng_def']
            for eng_def in eng_defs.split("\n"):
                word_eng_def = wp.WordBrief.Definition()
                pos_meaning = re.match('[a-zA-Z]+\.\s', eng_def)
                if pos_meaning is None:
                    word_eng_def.meaning = eng_def
                else:
                    word_eng_def.pos = pos_meaning.group()[:-1]
                    word_eng_def.meaning = eng_def[len(word_eng_def.pos):]
                word_brief.eng_definitions.extend([word_eng_def])
        if 'chn_def' in data:
            chn_defs = data['chn_def']
            for chn_def in chn_defs.split("\n"):
                word_chn_def = wp.WordBrief.Definition()
                pos_meaning = re.match('[a-zA-Z]+\.\s', chn_def)
                if pos_meaning is None:
                    word_chn_def.meaning = chn_def
                else:
                    word_chn_def.pos = pos_meaning.group()[:-1]
                    word_chn_def.meaning = chn_def[len(word_chn_def.pos):]
                word_brief.chn_definitions.extend([word_chn_def])

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
            word_brief.tags.extend(tag_list)

        return word_brief


class GetWordDetail(GetWordList):
    def get_detail(self, request_word, **kwargs):
        word_brief = self.get_list(request_word, **kwargs).word_briefs
        word_brief = word_brief[0]
        word_detail = wp.WordDetail()
        word_detail.word_brief.MergeFrom(word_brief)
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
                sentence_list = self.get_sentence(data['oxford_detail'])
                sentence_list = [wp.WordDetail.Sentence(
                    source=wp.WordDetail.Sentence.OXFORD, eng=s[0], chn=s[1])
                    for s in sentence_list]
                word_detail.sentences.extend(sentence_list)

            if 'collins_detail' in data:
                sentence_list = self.get_sentence(data['collins_detail'])
                sentence_list = [wp.WordDetail.Sentence(
                    source=wp.WordDetail.Sentence.COLLINS, eng=s[0], chn=s[1])
                    for s in sentence_list]
                word_detail.sentences.extend(sentence_list)

            if 'net_detail' in data:
                sentence_list = self.get_sentence(data['net_detail'])
                sentence_list = [wp.WordDetail.Sentence(
                    source=wp.WordDetail.Sentence.ONLINE, eng=s[0], chn=s[1])
                    for s in sentence_list]
                word_detail.sentences.extend(sentence_list)

            if len(word_detail.sentences) == 0:
                sentence_list = sql.request_iciba(request_word)
                sentence_list = [wp.WordDetail.Sentence(
                    source=wp.WordDetail.Sentence.ONLINE, eng=eng, chn=chn)
                    for eng, chn in sentence_list]
                word_detail.sentence.extend(sentence_list)

            if 'derivative' in data:
                derivative_list = [wp.WordDetail.Derivative(word=w, relation=r)
                                   for w, r in data['derivative'].items()]
                word_detail.derivatives.extend(derivative_list)
        return word_detail

    def get_sentence(self, sentences):
        sentence_list = sentences.split('\r\n')
        if sentence_list[-1] == '':
            sentence_list = sentence_list[:-1]
        split_sentence_list = []
        for s in sentence_list:
            s = s.split('\n')
            if len(s) == 1:
                s.append('')
            split_sentence_list.append(s)
        return split_sentence_list
