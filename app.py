import json

from flask import Flask, Response
from flask_restful import Resource, Api, reqparse, inputs
from google.protobuf.json_format import MessageToJson

import WordParsing
from Dict.stardict import DictCsv, LemmaDB
import requests

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('word', type=str, help='The word for query', required=True)
parser.add_argument('stem', type=inputs.boolean, help='whether get stem')


class Word(Resource):
    def get(self):
        args = parser.parse_args()

        word = args['word']
        is_stem = args['stem']
        word_processing = WordParsing.WordProcess(word, is_stem)
        #return MessageToJson(word_processing.word_detail)
        return Response(word_processing.word_detail.SerializeToString(), mimetype='application/x-protobuf')


api.add_resource(Word, '/')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
