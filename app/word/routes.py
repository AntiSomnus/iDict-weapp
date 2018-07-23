import json

from flask import Response
from flask_restful import Resource, inputs, reqparse
from google.protobuf.json_format import MessageToDict

from . import word_api
from .word_parsing import GetWordBrief, GetWordDetail, GetWordList

parser_word_brief = reqparse.RequestParser()
parser_word_brief.add_argument(
    'word', type=str, help='The word for query', required=True)
parser_word_brief.add_argument(
    'count', type=int, help='how much to receive', default=10)
parser_word_brief.add_argument(
    'tag', type=inputs.boolean, help='whether return tag', default=True)
parser_word_brief.add_argument(
    'pron', type=inputs.boolean, help='whether return pronunciation', default=True)
parser_word_brief.add_argument(
    'eng', type=inputs.boolean, help='whether return English definition', default=True)
parser_word_brief.add_argument(
    'json', type=inputs.boolean, help='whether get json', default=False)
parser_word_brief.add_argument(
    'indent', type=int, help='json incident', default=4)

parser_word_list = reqparse.RequestParser()
parser_word_list.add_argument(
    'word', type=str, help='The word for query', required=True)
parser_word_list.add_argument(
    'count', type=int, help='how much to receive', default=10)
parser_word_list.add_argument(
    'tag', type=inputs.boolean, help='whether return tag', default=True)
parser_word_list.add_argument(
    'pron', type=inputs.boolean, help='whether return pronunciation', default=True)
parser_word_list.add_argument(
    'eng', type=inputs.boolean, help='whether return English definition', default=True)
parser_word_list.add_argument(
    'json', type=inputs.boolean, help='whether get json', default=False)
parser_word_list.add_argument(
    'indent', type=int, help='json incident', default=4)

parser_word_detail = reqparse.RequestParser()
parser_word_detail.add_argument(
    'word', type=str, help='The word for query', required=True)
parser_word_detail.add_argument(
    'json', type=inputs.boolean, help='whether get json', default=False)
parser_word_detail.add_argument(
    'indent', type=int, help='json incident', default=4)


class WordBrief(Resource):
    def __init__(self):
        self.get_word_brief = GetWordBrief()

    def get(self):
        args = parser_word_brief.parse_args()
        word = args['word']
        is_json = args['json']
        indent = args['indent']
        word_brief_proto = self.get_word_brief.get_brief(word, kwargs=args)
        if word_brief_proto:
            if is_json:
                # print(MessageToDict(word_breif_proto))
                return Response(
                    json.dumps(MessageToDict(word_brief_proto), indent=indent,
                               ensure_ascii=False,
                               sort_keys=True).encode('utf-8').decode(),
                    content_type="application/json")
            return Response(word_brief_proto.SerializeToString(),
                            mimetype='application/x-protobuf')
        return Response(status=250)


class WordList(Resource):
    def __init__(self):
        self.get_word_list = GetWordList()

    def get(self):
        args = parser_word_list.parse_args()
        word = args['word']
        is_json = args['json']
        indent = args['indent']
        word_list_proto = self.get_word_list.get_list(word, kwargs=args)
        if word_list_proto:
            if is_json:
                # print(MessageToDict(word_list_proto))
                return Response(
                    json.dumps(MessageToDict(word_list_proto), indent=indent,
                               ensure_ascii=False,
                               sort_keys=True).encode('utf-8').decode(),
                    content_type="application/json")
            return Response(word_list_proto.SerializeToString(),
                            mimetype='application/x-protobuf')
        return Response(status=251)


class WordDetail(Resource):
    def __init__(self):
        self.get_word_detail = GetWordDetail()

    def get(self):
        args = parser_word_detail.parse_args()
        word = args['word']
        is_json = args['json']
        indent = args['indent']
        word_detail_proto = self.get_word_detail.get_detail(word)
        if word_detail_proto:
            if is_json:
                # print(MessageToDict(word_detail_proto))
                return Response(
                    json.dumps(MessageToDict(word_detail_proto), indent=indent,
                               ensure_ascii=False,
                               sort_keys=True).encode('utf-8').decode(),
                    content_type="application/json")
            return Response(word_detail_proto.SerializeToString(),
                            mimetype='application/x-protobuf')
        return Response(status=252)


word_api.add_resource(WordBrief, '/word/brief/')
word_api.add_resource(WordList, '/word/list/')
word_api.add_resource(WordDetail, '/word/detail/')
