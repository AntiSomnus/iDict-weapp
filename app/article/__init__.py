from flask import Blueprint
from flask_restful import Api

article_blueprint = Blueprint('article_status', __name__)
article_api = Api(article_blueprint)

from . import routes