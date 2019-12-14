from flask_restful import Resource
from flask_jwt_extended import create_access_token
from src.models import User, Post
from src.schemas import UserSchema, PostSchema
from src.middlewares import validate_with_schema, marshal_with_schema


user_schema = UserSchema()
post_schema = PostSchema()


class UserRegister(Resource):
    @validate_with_schema(user_schema)
    def post(self, data):
        user_in_db = User.get_by_email(data['email'])
        if user_in_db:
            return {'error': 'Email already registered'}

        user = User(**data)
        user.save()

        token = create_access_token(identity=user)

        return {'jwt_token': token}


class UserLogin(Resource):
    @validate_with_schema(user_schema, partial=True)
    def post(self, data):
        if not data.get('email') or not data.get('password'):
            return {'error': 'You need email and password to sign in'}
        user = User.get_by_email(data.get('email'))
        if not user:
            return {'error': 'invalid credentials'}, 400
        if not user.check_hash(data.get('password')):
            return {'error': 'invalid credentials'}, 400
        token = create_access_token(identity=user)
        return {'token': token}


class PostResource(Resource):
    @validate_with_schema(post_schema)
    @marshal_with_schema(post_schema)
    def post(self, data):
        post = Post(**data)

        return post
