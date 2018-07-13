import json

from flask import Response
from flask_restful import Resource, inputs, reqparse
from google.protobuf.json_format import MessageToDict, MessageToJson

from .WordParsing import WordProcess

from . import word_api

parser_word = reqparse.RequestParser()
parser_word.add_argument(
    'word', type=str, help='The word for query', required=True)
parser_word.add_argument('stem', type=inputs.boolean,
                         help='whether get stem', default=True)
parser_word.add_argument('json', type=inputs.boolean,
                         help='whether get json', default=False)
parser_word.add_argument('indent', type=int, help='json incident', default=4)


class Word(Resource):
    def get(self):
        args = parser_word.parse_args()

        word = args['word']
        is_stem = args['stem']
        is_json = args['json']
        indent = args['indent']
        word_processing = WordProcess(word, is_stem)
        if is_json:
            print(MessageToDict(word_processing.word_detail))
            return Response(
                json.dumps(MessageToDict(word_processing.word_detail), indent=indent,
                           ensure_ascii=False,
                           sort_keys=True
                           ).encode(
                    'utf-8').decode(),
                content_type="application/json")
        return Response(word_processing.word_detail.SerializeToString(), mimetype='application/x-protobuf')


word_api.add_resource(Word, '/')
