from flask import Blueprint
from flask_restful import Api

support_blueprint = Blueprint('support', __name__)
support_api = Api(support_blueprint)

from . import routes
