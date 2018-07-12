import json

from flask import Flask, Response
from flask_restful import Resource, Api, reqparse, inputs
from google.protobuf.json_format import MessageToJson, MessageToDict

import WordParsing
from ArticleParsing import get_article_list, get_article_detail
from Dict.stardict import DictCsv, LemmaDB
import requests

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app)

parser_word = reqparse.RequestParser()
parser_word.add_argument('word', type=str, help='The word for query', required=True)
parser_word.add_argument('stem', type=inputs.boolean, help='whether get stem', default=True)
parser_word.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
parser_word.add_argument('indent', type=int, help='json incident', default=4)

parser_article_list = reqparse.RequestParser()
parser_article_list.add_argument('page', type=int, help='page_number', default=1)
parser_article_list.add_argument('count', type=int, help='count number', default=10)
parser_article_list.add_argument('source', type=str, help='source plain name', default=None)
parser_article_list.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
parser_article_list.add_argument('indent', type=int, help='json incident', default=4)

parser_article_detail = reqparse.RequestParser()
parser_article_detail.add_argument('uri', type=str, help='article uri', required=True)
parser_article_detail.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
parser_article_detail.add_argument('indent', type=int, help='json incident', default=4)


class Word(Resource):

    def get(self):
        args = parser_word.parse_args()

        word = args['word']
        is_stem = args['stem']
        is_json = args['json']
        indent = args['indent']
        word_processing = WordParsing.WordProcess(word, is_stem)
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


class ArticleList(Resource):

    def get(self):
        args = parser_article_list.parse_args()
        page = args['page']
        count = args['count']
        source_title = args['source']

        is_json = args['json']
        indent = args['indent']

        article_list = get_article_list(page=page, count=count, source_title=source_title)

        if is_json:
            print(MessageToDict(article_list))
            return Response(
                json.dumps(MessageToDict(article_list), indent=indent,
                           ensure_ascii=False,
                           sort_keys=True
                           ).encode(
                    'utf-8').decode(),
                content_type="application/json")
        return Response(article_list.SerializeToString(), mimetype='application/x-protobuf')


class ArticleDetail(Resource):

    def get(self):
        args = parser_article_detail.parse_args()
        uri = args['uri']
        is_json = args['json']
        indent = args['indent']

        article_detail = get_article_detail(article_uri=uri)

        if is_json:
            print(MessageToDict(article_detail))
            return Response(
                json.dumps(MessageToDict(article_detail), indent=indent,
                           ensure_ascii=False,
                           sort_keys=True
                           ).encode(
                    'utf-8').decode(),
                content_type="application/json")
        return Response(article_detail.SerializeToString(), mimetype='application/x-protobuf')


api.add_resource(Word, '/')
api.add_resource(ArticleList, '/articleList')
api.add_resource(ArticleDetail, '/articleDetail')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
