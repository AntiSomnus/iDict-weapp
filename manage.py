from app import create_app
from flask_script import Manager

manager = Manager(create_app())

if __name__ == '__main__':
    manager.run()
