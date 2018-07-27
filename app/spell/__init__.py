from flask import Blueprint
from flask_restful import Api

spell_blueprint = Blueprint('spell', __name__)
spell_api = Api(spell_blueprint)

from . import routes
