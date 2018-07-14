import sqlalchemy
from flask import Flask

user = ''
passwd = ''
host = ''
port = ''
db = ''

user = 'root'
passwd = '***REMOVED***'
host = 'localhost'
port = '3306'
db = 'ireading'

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
