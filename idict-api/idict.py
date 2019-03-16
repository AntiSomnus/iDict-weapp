import json
from configparser import ConfigParser

import requests
from flask import Flask, Response
from flask_restful import Resource, Api, reqparse, inputs
from pymongo import MongoClient
from redis import Redis
from word import mongo

SECTION = "idict-db"

conf = ConfigParser()
conf.read("conf.ini")
user = conf.get(SECTION, 'user')
pwd = conf.get(SECTION, 'pwd')
host = conf.get(SECTION, 'host')
port = int(conf.get(SECTION, 'port'))
db = conf.get(SECTION, 'db')
redis_brief_port = int(conf.get(SECTION, 'redis_brief_port'))
redis_rank_port = int(conf.get(SECTION, 'redis_rank_port'))

app = Flask(__name__)
api = Api(app)

client = MongoClient(host=host,
                     port=port,
                     username=user,
                     password=pwd,
                     authSource='admin',
                     )
mongo = mongo.Mongo(client[db].chn, client[db].word_entire, client[db].word_mini, client.idict.support,
                    Redis(host=host, port=redis_brief_port, db=0),
                    Redis(host=host, port=redis_rank_port, db=0))


class WordBrief(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('word', type=str, help='The word for query', required=True)
        self.parser.add_argument('tag', type=inputs.boolean, help='whether return tag', default=True)
        self.parser.add_argument('pron', type=inputs.boolean, help='whether return pronunciation', default=True)
        self.parser.add_argument('eng', type=inputs.boolean, help='whether return English definition',
                                 default=True)
        self.parser.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
        self.parser.add_argument('indent', type=int, help='json incident', default=4)
        self.parser.add_argument('traceLemma', type=inputs.boolean, help='whether trace back to lemma',
                                 default=True)

    def get(self):
        args = self.parser.parse_args()
        word = args['word']
        is_json = args['json']
        indent = args['indent']
        is_trace_lemma = args['traceLemma']
        result = mongo.get_word_brief(word, is_protobuf=not is_json, is_trace_lemma=is_trace_lemma)

        if not result:
            return Response(status=250)
        if is_json:
            return Response(
                json.dumps(result, indent=indent, ensure_ascii=False, sort_keys=True),
                content_type="application/json")
        else:
            return Response(result.SerializeToString(), mimetype='application/x-protobuf')


class WordDetail(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('word', type=str, help='The word for query', required=True)
        self.parser.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
        self.parser.add_argument('indent', type=int, help='json incident', default=4)

    def get(self):
        args = self.parser.parse_args()
        word = args['word']
        is_json = args['json']
        indent = args['indent']
        result = mongo.get_word_detail(word, is_protobuf=not is_json)
        if not result:
            return Response(status=252)
        if is_json:
            return Response(
                json.dumps(result, indent=indent, ensure_ascii=False, sort_keys=True),
                content_type="application/json")
        else:
            return Response(result.SerializeToString(), mimetype='application/x-protobuf')


class WordList(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('word', type=str, help='The word for query', required=True)
        self.parser.add_argument('count', type=int, help='how much to receive', default=10)
        self.parser.add_argument('tag', type=inputs.boolean, help='whether return tag', default=True)
        self.parser.add_argument('pron', type=inputs.boolean, help='whether return pronunciation', default=True)
        self.parser.add_argument('eng', type=inputs.boolean, help='whether return English definition',
                                 default=True)
        self.parser.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
        self.parser.add_argument('indent', type=int, help='json incident', default=4)

    def get(self):
        args = self.parser.parse_args()
        word = args['word']
        is_json = args['json']
        indent = args['indent']
        result = mongo.get_word_list(word, is_protobuf=not is_json, is_suggestion=len(word) > 3, )
        if is_json:
            return Response(
                json.dumps(result, indent=indent, ensure_ascii=False, sort_keys=True),
                content_type="application/json")
        else:
            return Response(result.SerializeToString(), mimetype='application/x-protobuf')


class WordExample(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('word', type=str, help='The word for query', required=True)
        self.parser.add_argument('count', type=int, help='max count for example', default=5)

    def get(self):
        args = self.parser.parse_args()
        word = args['word']
        count = args['count']
        payload = {'maxResults': count, 'query': word}
        if word:
            result = requests.get("https://corpus.vocabulary.com/api/1.0/examples.json", params=payload)
            return Response(result.text, content_type="application/json")


class BugReporter(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('type', type=str, )
        self.parser.add_argument('details', type=str)

    def post(self):
        args = self.parser.parse_args()
        word, detail = args['details'].split('\r\n')
        mongo.add_support(word, args['type'], detail)
        return Response(status=200)


class ChnDetail(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('chn', type=str, help='The chn for query', required=True)
        self.parser.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
        self.parser.add_argument('indent', type=int, help='json incident', default=4)

    def get(self):
        args = self.parser.parse_args()
        chn = args['chn']
        is_json = args['json']
        indent = args['indent']
        result = mongo.get_chn_detail(chn, is_protobuf=not is_json)
        if not result:
            return Response(status=252)
        if is_json:
            return Response(
                json.dumps(result, indent=indent, ensure_ascii=False, sort_keys=True),
                content_type="application/json")
        else:
            return Response(result.SerializeToString(), mimetype='application/x-protobuf')


class ChnList(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('word', type=str, help='The word for query', required=True)
        self.parser.add_argument('count', type=int, help='how much to receive', default=10)
        self.parser.add_argument('json', type=inputs.boolean, help='whether get json', default=False)
        self.parser.add_argument('indent', type=int, help='json incident', default=4)

    def get(self):
        args = self.parser.parse_args()
        word = args['word']
        is_json = args['json']
        indent = args['indent']
        count = args['count']
        result = mongo.get_chn_list(word, is_protobuf=not is_json, limit_count=count)
        if is_json:
            return Response(
                json.dumps(result, indent=indent, ensure_ascii=False, sort_keys=True),
                content_type="application/json")
        else:
            return Response(result.SerializeToString(), mimetype='application/x-protobuf')


api.add_resource(WordList, '/word/list/')
api.add_resource(ChnList, '/chn/list/')
api.add_resource(ChnDetail, '/chn/detail/')
api.add_resource(WordDetail, '/word/detail/')
api.add_resource(WordBrief, '/word/brief/')
api.add_resource(WordExample, '/word/example/')
api.add_resource(BugReporter, '/support/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
