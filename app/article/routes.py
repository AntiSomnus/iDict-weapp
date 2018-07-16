import json

from flask import Response
from flask_restful import Resource, inputs, reqparse
from google.protobuf.json_format import MessageToDict

from . import article_api
from .article_parsing import get_article_detail, get_article_list

parser_article_list = reqparse.RequestParser()
parser_article_list.add_argument(
    'page', type=int, help='page_number', default=1)
parser_article_list.add_argument(
    'count', type=int, help='count number', default=10)
parser_article_list.add_argument(
    'keywords', type=str, help='keywords ', default=None)
parser_article_list.add_argument(
    'source', type=str, help='source plain name', default=None)
parser_article_list.add_argument(
    'json', type=inputs.boolean, help='whether get json', default=False)
parser_article_list.add_argument(
    'indent', type=int, help='json incident', default=4)

parser_article_detail = reqparse.RequestParser()
parser_article_detail.add_argument(
    'uri', type=str, help='article uri', required=True)
parser_article_detail.add_argument(
    'json', type=inputs.boolean, help='whether get json', default=False)
parser_article_detail.add_argument(
    'indent', type=int, help='json incident', default=4)


class ArticleList(Resource):
    def get(self):
        args = parser_article_list.parse_args()
        page = args['page']
        count = args['count']
        source_title = args['source']
        keywords = args['keywords']
        is_json = args['json']
        indent = args['indent']

        article_list = get_article_list(page=page, count=count,
                                        source_title=source_title,
                                        keywords=keywords)

        if is_json:
            # print(MessageToDict(article_list))
            return Response(
                json.dumps(MessageToDict(article_list), indent=indent,
                           ensure_ascii=False,
                           sort_keys=True).encode('utf-8').decode(),
                           content_type="application/json")
        return Response(article_list.SerializeToString(),
                        mimetype='application/x-protobuf')


class ArticleDetail(Resource):
    def get(self):
        args = parser_article_detail.parse_args()
        uri = args['uri']
        is_json = args['json']
        indent = args['indent']

        article_detail = get_article_detail(article_uri=uri)

        if is_json:
            # print(MessageToDict(article_detail))
            return Response(
                json.dumps(MessageToDict(article_detail), indent=indent,
                           ensure_ascii=False,
                           sort_keys=True).encode('utf-8').decode(),
                           content_type="application/json")
        return Response(article_detail.SerializeToString(),
                        mimetype='application/x-protobuf')


article_api.add_resource(ArticleList, '/article/list')
article_api.add_resource(ArticleDetail, '/article/detail')
