from flask import Flask
from flask_restful import Api
from src.extensions import db, bcrypt, jwt, cors
from src.config import app_config
from src.exceptions import InvalidUsage, error_handler
from src.resources import UserRegister, UserLogin, UserMe, UserResource, \
    PostsResource, PostResource, PostsByUserResource, \
    CommentsResource, CommentResource, \
    FavoriteResource, FavoritePostsByUserResource, TagResource


def create_app(env_name):
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    api = Api(app)

    bcrypt.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    app.errorhandler(InvalidUsage)(error_handler)

    api.add_resource(UserRegister, '/register')
    api.add_resource(UserLogin, '/login')
    api.add_resource(UserMe, '/me')
    api.add_resource(UserResource, '/@<string:username>')
    api.add_resource(PostsByUserResource, '/@<string:username>/posts')
    api.add_resource(
        FavoritePostsByUserResource,
        '/@<string:username>/favorites'
    )
    api.add_resource(TagResource, '/tags')
    api.add_resource(PostsResource, '/posts')
    api.add_resource(PostResource, '/posts/<int:post_id>')
    api.add_resource(FavoriteResource, '/posts/<int:post_id>/favorite')
    api.add_resource(CommentsResource, '/posts/<int:post_id>/comments')
    api.add_resource(
        CommentResource,
        '/posts/<int:post_id>/comments/<int:comment_id>'
    )

    @app.route('/', methods=['GET'])
    def index():
        return 'Welcome'

    return app
