from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, current_user
from src.models import User, Post
from src.schemas import user_schema, login_schema, post_schema, posts_schema
from src.middlewares import validate_with_schema, marshal_with_schema
from src.utils import error_response, success_response


class UserRegister(Resource):
    @validate_with_schema(user_schema)
    def post(self, data):
        user_in_db = User.get_by_email(data['email'])
        if user_in_db:
            return error_response('Email already registered')

        user = User(**data)
        user.save()

        token = create_access_token(identity=user)

        return success_response({'token': token})


class UserLogin(Resource):
    @validate_with_schema(login_schema)
    def post(self, data):
        user = User.get_by_email(data['email'])

        if not user or not user.check_hash(data['password']):
            return error_response('invalid credentials')

        token = create_access_token(identity=user)
        return success_response({'token': token})


class UserMe(Resource):
    @jwt_required
    @validate_with_schema(user_schema, partial=True)
    @marshal_with_schema(user_schema)
    def put(self, data):
        user = current_user
        user.update(**data)
        return user

    @jwt_required
    @marshal_with_schema(user_schema)
    def get(self):
        return current_user


class PostsResource(Resource):
    @jwt_required
    @validate_with_schema(post_schema)
    @marshal_with_schema(post_schema)
    def post(self, data):
        post = Post(**data, owner_id=current_user.id)
        post.save()

        return post

    @marshal_with_schema(posts_schema)
    def get(self):
        posts = Post.get_all()

        return posts


class PostResource(Resource):
    @marshal_with_schema(post_schema)
    def get(self, post_id):
        post = Post.get_one(post_id)
        if not post:
            return error_response('Post not found', 404)

        return post

    @jwt_required
    def delete(self, post_id):
        user = current_user
        post = Post.get_one(post_id)

        if not post:
            return error_response('Post not found', 404)
        if post.owner_id != user.id:
            return error_response('Permission denied', 403)

        post.delete()
        return success_response({'deleted': post.id})
