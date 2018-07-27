from flask import Response
from flask_restful import Resource, reqparse

from . import spell_api
from .spell import SpellCorrector

parser_spell = reqparse.RequestParser()
parser_spell.add_argument(
    'word', type=str, help='input word', required=True)
parser_spell.add_argument(
    'type', type=int, help='return type', default=1)

spell_corrector = SpellCorrector()


class Corrector(Resource):
    def get(self):
        args = parser_spell.parse_args()
        if args['type'] == 1:
            candidates = spell_corrector.candidates(args['word'])
            return candidates
        if args['type'] == 2:
            correction = spell_corrector.correction(args['word'])
            return {'correction': correction}
        return Response(status=260)


spell_api.add_resource(Corrector, '/spell/')
