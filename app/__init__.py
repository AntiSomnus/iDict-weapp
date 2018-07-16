from configparser import ConfigParser
from os import path

import sqlalchemy
from flask import Flask


fp = path.join('.', 'conf.ini')
conf = ConfigParser()
conf.read(fp)
user = conf.get('ireading-db', 'user')
passwd = conf.get('ireading-db', 'passwd')
host = conf.get('ireading-db', 'host')
port = conf.get('ireading-db', 'port')
db = conf.get('ireading-db', 'db')

engine_str = 'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}'.format(
    user=user, passwd=passwd, host=host, port=port, db=db)
engine = sqlalchemy.create_engine(engine_str, echo=False)
conn = engine.connect()


def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    from .article import article_blueprint
    from .word import word_blueprint
    app.register_blueprint(article_blueprint)
    app.register_blueprint(word_blueprint)

    return app
