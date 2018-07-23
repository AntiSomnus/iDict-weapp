import re

from . import WordProto_pb2 as wp
from .. import conn
from .sql import OperateDB

sql = OperateDB(conn)


class GetWordBrief(object):
    def get_brief(self, request_word, **kwargs):
        result = sql.select_brief(request_word, **kwargs)
        if result['status']:
            return self.process_brief(result['data'])
        else:
            return False

    def process_brief(self, data):
        word_brief = wp.WordBrief()
        word_brief.word_in = data['word_in']
        word_brief.word_out = data['word']

        if 'lemma' in data:
            word_lemma = wp.WordBrief.Lemma()
            word_lemma.lemma = data['lemma']['word']
            word_lemma.relation = data['lemma']['relation']
            word_brief.word_out = data['lemma']['word']
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
            for eng_def in eng_defs.replace('\\n', '\n').split('\n'):
                word_eng_def = wp.WordBrief.Definition()
                pos_meaning = re.match(r'[a-zA-Z]+\.\s', eng_def)
                if pos_meaning is None:
                    word_eng_def.meaning = eng_def.strip()
                else:
                    word_eng_def.pos = pos_meaning.group()[:-1]
                    word_eng_def.meaning = eng_def[
                        len(word_eng_def.pos):].strip()
                word_brief.eng_definitions.extend([word_eng_def])
        if 'chn_def' in data:
            chn_defs = data['chn_def']
            for chn_def in chn_defs.replace('\\n', '\n').split('\n'):
                word_chn_def = wp.WordBrief.Definition()
                pos_meaning = re.match(r'[a-zA-Z]+\.\s', chn_def)
                if pos_meaning is None:
                    word_chn_def.meaning = chn_def.strip()
                else:
                    word_chn_def.pos = pos_meaning.group()[:-1]
                    word_chn_def.meaning = chn_def[
                        len(word_chn_def.pos):].strip()
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


class GetWordList(GetWordBrief):
    def get_list(self, request_word, **kwargs):
        word_list = wp.WordList()
        result = sql.select_list(request_word, **kwargs)
        if result['status']:
            for data in result['data']:
                word_list.word_briefs.extend([self.process_brief(data)])
            return word_list
        else:
            return False


class GetWordDetail(GetWordBrief):
    def get_detail(self, request_word):
        result = sql.select_detail(request_word)
        if result['status'] == False:
            return False
        word_brief = self.process_brief(result['brief'])
        word_detail = wp.WordDetail()
        word_detail.word_brief.MergeFrom(word_brief)

        data = result['data']

        if 'collins' in data:
            word_detail.collins = data['collins']

        if 'bnc' in data:
            word_detail.bnc = data['bnc']

        if 'frq' in data:
            word_detail.frq = data['frq']

        if 'oxford_detail' in data:
            sentences = self.get_sentence(data['oxford_detail'])
            sentences = [wp.WordDetail.SentenceList.Sentence(eng=s[0], chn=s[1])
                         for s in sentences]
            sentence_list = wp.WordDetail.SentenceList()
            sentence_list.source = wp.WordDetail.SentenceList.OXFORD
            sentence_list.sentences.extend(sentences)
            word_detail.sentence_lists.extend([sentence_list])

        if 'cambridge_detail' in data:
            sentences = self.get_sentence(data['cambridge_detail'])
            sentences = [wp.WordDetail.SentenceList.Sentence(eng=s[0], chn=s[1])
                         for s in sentences]
            sentence_list = wp.WordDetail.SentenceList()
            sentence_list.source = wp.WordDetail.SentenceList.CAMBRIDGE
            sentence_list.sentences.extend(sentences)
            word_detail.sentence_lists.extend([sentence_list])

        if 'longman_detail' in data:
            sentences = self.get_sentence(data['longman_detail'])
            sentences = [wp.WordDetail.SentenceList.Sentence(eng=s[0], chn=s[1])
                         for s in sentences]
            sentence_list = wp.WordDetail.SentenceList()
            sentence_list.source = wp.WordDetail.SentenceList.LONGMAN
            sentence_list.sentences.extend(sentences)
            word_detail.sentence_lists.extend([sentence_list])

        if 'collins_detail' in data:
            sentences = self.get_sentence(data['collins_detail'])
            sentences = [wp.WordDetail.SentenceList.Sentence(eng=s[0], chn=s[1])
                         for s in sentences]
            sentence_list = wp.WordDetail.SentenceList()
            sentence_list.source = wp.WordDetail.SentenceList.COLLINS
            sentence_list.sentences.extend(sentences)
            word_detail.sentence_lists.extend([sentence_list])

        if 'net_detail' in data:
            sentences = self.get_sentence(data['net_detail'])
            sentences = [wp.WordDetail.SentenceList.Sentence(eng=s[0], chn=s[1])
                         for s in sentences]
            sentence_list = wp.WordDetail.SentenceList()
            sentence_list.source = wp.WordDetail.SentenceList.ONLINE
            sentence_list.sentences.extend(sentences)
            word_detail.sentence_lists.extend([sentence_list])

        if len(word_detail.sentence_lists) == 0:
            sentences = sql.request_iciba(request_word)
            sentences = [wp.WordDetail.SentenceList.Sentence(eng=eng, chn=chn)
                         for eng, chn in sentences]
            sentence_list = wp.WordDetail.SentenceList()
            sentence_list.source = wp.WordDetail.SentenceList.ONLINE
            sentence_list.sentences.extend(sentences)
            word_detail.sentence_lists.extend([sentence_list])

        if 'derivative' in data:
            derivative_list = [wp.WordDetail.Derivative(word=w, relation=r)
                               for w, r in data['derivative'].items()]
            word_detail.derivatives.extend(derivative_list)
        return word_detail

    def get_sentence(self, sentence_lists):
        sentences = sentence_lists.split('\r\n')
        if sentences[-1] == '':
            sentences = sentences[:-1]
        split_sentence_list = []
        for s in sentences:
            s = s.split('\n')
            if len(s) == 1:
                s.append('')
            split_sentence_list.append(s)
        return split_sentence_list
