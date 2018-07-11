import json

from flask import Flask, Response
from flask_restful import Resource, Api, reqparse, inputs
from google.protobuf.json_format import MessageToJson, MessageToDict

import WordParsing
from Dict.stardict import DictCsv, LemmaDB
import requests

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('word', type=str, help='The word for query', required=True)
parser.add_argument('stem', type=inputs.boolean, help='whether get stem', default=True)
parser.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
parser.add_argument('indent', type=int, help='json incident', default=4)


class Word(Resource):
    def get(self):
        args = parser.parse_args()

        word = args['word']
        is_stem = args['stem']
        is_json = args['json']
        indent = args['indent']
        word_processing = WordParsing.WordProcess(word, is_stem)
        if is_json:
            return Response(
                json.dumps(MessageToDict(word_processing.word_detail), indent=indent, ensure_ascii=False).encode(
                    'utf-8').decode(),
                content_type="application/json")
        return Response(word_processing.word_detail.SerializeToString(), mimetype='application/x-protobuf')


api.add_resource(Word, '/')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
