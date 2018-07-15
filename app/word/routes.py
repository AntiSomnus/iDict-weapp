import json

from flask import Response
from flask_restful import Resource, inputs, reqparse
from google.protobuf.json_format import MessageToDict

from . import word_api
from .WordParsing import GetWordDetail, GetWordList

parser_word_list = reqparse.RequestParser()
parser_word_list.add_argument(
    'word', type=str, help='The word for query', required=True)
parser_word_list.add_argument(
    'count', type=int, help='how much to receive', default=10)
parser_word_list.add_argument(
    'divide', type=inputs.boolean, help='whether divide meaning', default=False)
parser_word_list.add_argument(
    'taglist', type=inputs.boolean, help='whether return taglist', default=True)
parser_word_list.add_argument(
    'json', type=inputs.boolean, help='whether get json', default=False)
parser_word_list.add_argument(
    'indent', type=int, help='json incident', default=4)

parser_word = reqparse.RequestParser()
parser_word.add_argument(
    'word', type=str, help='The word for query', required=True)
parser_word.add_argument(
    'stem', type=inputs.boolean, help='whether get stem', default=True)
parser_word.add_argument(
    'json', type=inputs.boolean, help='whether get json', default=False)
parser_word.add_argument(
    'indent', type=int, help='json incident', default=4)


class WordList(Resource):
    def get(self):
        args = parser_word_list.parse_args()
        word = args['word']
        count = args['count']
        is_json = args['json']
        is_divide = args['divide']
        is_tag_list = args['taglist']
        indent = args['indent']
        word_listing = GetWordList()
        word_list_proto = word_listing.get_word_list(
            word, count, is_divide, is_tag_list)
        if is_json:
            print(MessageToDict(word_list_proto))
            return Response(
                json.dumps(MessageToDict(word_list_proto), indent=indent,
                           ensure_ascii=False,
                           sort_keys=True
                           ).encode(
                    'utf-8').decode(),
                content_type="application/json")
        return Response(word_list_proto.SerializeToString(), mimetype='application/x-protobuf')


class WordDetail(Resource):
    def get(self):
        args = parser_word.parse_args()
        word = args['word']
        is_stem = args['stem']
        is_json = args['json']
        indent = args['indent']
        word_processing = GetWordDetail(word, is_stem)
        if is_json:
            print(MessageToDict(word_processing.word_detail))
            return Response(
                json.dumps(MessageToDict(word_processing.word_detail), indent=indent,
                           ensure_ascii=False,
                           sort_keys=True
                           ).encode(
                    'utf-8').decode(),
                content_type="application/json")
        return Response(word_processing.word_detail.SerializeToString(),
                        mimetype='application/x-protobuf')


word_api.add_resource(WordDetail, '/worddetail')
word_api.add_resource(WordList, '/wordlist')
