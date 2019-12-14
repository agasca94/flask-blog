from flask import Flask
from flask_restful import Api
from src.extensions import db, bcrypt, jwt
from src.config import app_config
from src.resources import UserRegister, UserLogin, PostResource


def create_app(env_name):
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    api = Api(app)

    bcrypt.init_app(app)
    db.init_app(app)
    jwt.init_app(app)

    api.add_resource(UserRegister, '/register')
    api.add_resource(UserLogin, '/login')
    api.add_resource(PostResource, '/posts')

    @app.route('/', methods=['GET'])
    def index():
        return 'Welcome'

    return app
