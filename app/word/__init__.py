from flask import Blueprint
from flask_restful import Api

word_blueprint = Blueprint('word_status', __name__)
word_api = Api(word_blueprint)

from . import routes
