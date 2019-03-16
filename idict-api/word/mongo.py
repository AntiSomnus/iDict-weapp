import time
from typing import List

from google.protobuf import json_format
from google.protobuf.json_format import MessageToDict
from pymongo import collection, ASCENDING
from redis import Redis
import heapq
import json
from .WordProto_pb2 import WordDetail, WordBrief, WordList, ChnDetail, ChnList
from . import suggestion


class Mongo:
    def __init__(self,
                 chn_collection: collection.Collection,
                 word_collection: collection.Collection,
                 word_mini_collection: collection.Collection,
                 support_collection: collection.Collection,
                 redis_brief: Redis,
                 redis_rank: Redis):
        self.chn_collection = chn_collection
        self.word_collection = word_collection
        self.word_mini_collection = word_mini_collection
        self.support_collection = support_collection
        self.word_mini_rank = self.word_collection.find({}, {"word": 1, "rank": 1, "_id": 0})
        self.redis_brief = redis_brief
        self.redis_rank = redis_rank
        self.spell_cost = suggestion.Suggestion()
        self.total_lower = {lower.decode() for lower in self.redis_rank.keys()}

    def get_word_detail(self, word: str, is_protobuf: bool = False):
        result = self.word_collection.find_one({"lower": word.lower()}, {"word": 1, "wordDetail": 1, "_id": 0})
        if result is None:
            return None
        word_detail = result['wordDetail']
        word_detail['wordBrief']['wordIn'] = word
        word_detail['wordBrief']['wordOut'] = result['word']
        if is_protobuf:
            word_detail_msg = WordDetail()
            return json_format.Parse(json.dumps(word_detail), word_detail_msg, ignore_unknown_fields=False)

        else:
            return word_detail

    def get_word_brief(self, word: str, is_protobuf: bool = False, is_trace_lemma: bool = False,
                       is_only_redis=False,
                       keys_to_be_removed: List = []):
        """
        query from redis first
        :param word:
        :param is_protobuf:
        :param is_trace_lemma: if True, return the brief of `lemma`
        :return:
        """
        lower = word.lower()
        result = self.redis_brief.get(lower)
        if result is not None:  # find word in redis
            word_brief_msg = WordBrief()
            word_brief_msg.ParseFromString(result)
            if is_trace_lemma:  # if trace lemma
                relation = word_brief_msg.lemma.relation
                if relation:  # lemma exist, then get lemma brief, set relation
                    lemma = word_brief_msg.lemma.lemma
                    word_brief_msg = self.get_word_brief(lemma, is_protobuf=True, is_trace_lemma=False)
                    word_brief_msg.lemma.relation = relation
                    word_brief_msg.lemma.lemma = lemma
                    word_brief_msg.wordOut = lemma
            word_brief_msg.wordIn = word  # finally set word in
            self.remove_from_protobuf_msg(word_brief_msg, keys_to_be_removed)
            if is_protobuf:
                return word_brief_msg
            else:
                return MessageToDict(word_brief_msg)
        else:  # not find in redis, then go to mongodb
            if is_only_redis:
                return None
            result = self.word_collection.find_one({"lower": lower},
                                                   {"word": 1,
                                                    "wordDetail.wordBrief": 1,
                                                    "_id": 0})
            if result is None:
                return None
            word_out, word_brief = result['word'], result['wordDetail']['wordBrief']
            if is_trace_lemma:
                lemma_obj = word_brief['lemma']
                if 'relation' in lemma_obj:
                    lemma = lemma_obj['lemma']
                    relation = lemma_obj['relation']
                    word_brief = self.get_word_brief(word=lemma, is_protobuf=False, is_trace_lemma=False)
                    word_brief['lemma']['relation'] = relation
            word_brief['wordIn'] = word
            self.remove_from_dict(word_brief, keys_to_be_removed)
            if is_protobuf:
                word_brief_msg = WordBrief()
                return json_format.Parse(json.dumps(word_brief), word_brief_msg, ignore_unknown_fields=False)

            else:
                return word_brief

    def get_chn_detail(self, chn: str, is_protobuf: bool = False):
        result = self.chn_collection.find_one(
            {
                'chn': chn,
            },
            {
                "chn": 1,
                "chnDetail": 1,
                "_id": 0
            })
        if result is None:
            return None
        if is_protobuf:
            chn_detail_msg = ChnDetail()
            return json_format.Parse(json.dumps(result['chnDetail']), chn_detail_msg, ignore_unknown_fields=False)

        else:
            return result['chnDetail']

    def get_chn_list(self, chn: str, is_protobuf: bool = False, limit_count=10):
        results = self.chn_collection.find(
            {
                'chn': {'$regex': '^%s' % chn},
            },
            {
                "chnDetail.meanings.words": 1,
                "chnDetail.chn": 1,
                "_id": 0
            }).limit(limit_count)
        word_list = {'wordBriefs': []}
        if results:
            for result in results:
                word_list['wordBriefs'].append({
                    'wordOut': result['chnDetail']['chn'],
                    'chnDefinitions': [{
                        'meaning': "; ".join(x['words'])
                    } for x in result['chnDetail']['meanings'] if 'words' in x]
                })
        if is_protobuf:
            word_list_msg = WordList()
            return json_format.Parse(json.dumps(word_list), word_list_msg, ignore_unknown_fields=False)

        else:
            return word_list

    @staticmethod
    def remove_from_dict(d: dict, keys_to_be_removed):
        for key in keys_to_be_removed:
            if key in d:
                del d[key]

    @staticmethod
    def remove_from_protobuf_msg(m, keys_to_be_removed):
        for key in keys_to_be_removed:
            try:
                m.ClearField(key)
            except ValueError:  # no such field
                pass

    @staticmethod
    def get_word_brief_from_mongo_result(word_in: str, result: dict) -> dict:
        word_brief = result['wordDetail']['wordBrief']
        word_brief['wordIn'] = word_in
        word_brief['wordOut'] = result['word']
        return word_brief

    def get_word_list(self, word: str,
                      is_protobuf: bool = False,
                      limit_count: int = 10,
                      is_suggestion: bool = False,
                      keys_to_be_removed: List[str] = ('engDefinitions', 'ukPron', 'usPron', 'lemma')):

        word_list = {"wordBriefs": []}
        lower = word.lower()
        collection_to_use = self.word_mini_collection if len(lower) < 4 else self.word_collection
        results = collection_to_use.find(
            {
                'lower': {'$regex': '^%s' % lower},
            },
            {
                "word": 1,
                "wordDetail.wordBrief": 1,
                "_id": 0
            }).sort([("rank", ASCENDING), ("lower", ASCENDING)]).limit(limit_count)
        if results:  # results not none, check whether the word in the list
            is_current_shown = False
            for result in results:
                parsed = self.get_word_brief_from_mongo_result(word, result)
                self.remove_from_dict(parsed, keys_to_be_removed)
                if parsed['wordOut'].lower() == lower:
                    word_list["wordBriefs"].insert(0, parsed)
                    is_current_shown = True
                else:
                    word_list["wordBriefs"].append(parsed)

            if not is_current_shown:  # if not in list, fetch from db
                exact_word = self.get_word_brief(word, False, False)
                if exact_word is not None:
                    self.remove_from_dict(exact_word, keys_to_be_removed)
                    word_list["wordBriefs"].insert(0, exact_word)
        if is_suggestion:
            word_list["wordSuggestions"] = self.suggestion(word)

        if is_protobuf:
            word_list_msg = WordList()
            return json_format.Parse(json.dumps(word_list), word_list_msg, ignore_unknown_fields=False)

        return word_list

    @staticmethod
    def edits1(word) -> set:
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    @staticmethod
    def edits2(word) -> set:
        return set(e2 for e1 in Mongo.edits1(word) for e2 in Mongo.edits1(e1))

    def suggestion(self, word: str, count: int = 10, is_protobuf=False):
        lower = word.lower()
        set1 = Mongo.edits1(lower)
        set2 = Mongo.edits2(lower)
        s = set1 | set2
        s.discard(lower)
        heap_l = []
        word_suggestions = []
        candidates = s & self.total_lower
        for candidate in candidates:
            heapq.heappush(heap_l, (self.spell_cost.get_cost(word, candidate), candidate))
        while len(word_suggestions) < count and len(heap_l) > 0:
            cost, lower = heapq.heappop(heap_l)
            word_suggestion = self.get_word_brief(lower, is_protobuf=is_protobuf, is_trace_lemma=False,
                                                  is_only_redis=True,
                                                  keys_to_be_removed=['ukPron', 'usPron', 'engDefinitions',
                                                                      'lemma'])
            if word_suggestion:
                word_suggestions.append(word_suggestion)

        return word_suggestions

    def add_support(self, word: str, support_type: str, detail: str):
        self.support_collection.insert_one({'word': word, 'type': support_type, 'detail': detail})
