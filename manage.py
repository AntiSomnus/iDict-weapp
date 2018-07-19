from app import create_app
from flask_script import Manager
from flask_compress import Compress

app = create_app()
app.config['COMPRESS_MIMETYPES'] = [
    'text/html',
    'text/css',
    'text/xml',
    'application/json',
    'application/javascript',
    'application/x-protobuf',
]
app.config['COMPRESS_LEVEL'] = 2
app.debug = True
Compress(app)
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
