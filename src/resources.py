from flask import request as req
from flask_restful import Resource
from flask_jwt_extended import create_access_token, current_user, \
    jwt_required, jwt_optional
from src.models import User, Post, Comment
from src.exceptions import InvalidUsage
from src.schemas import login_schema, user_schema, UserSchema, \
    post_schema, posts_schema,\
    comment_schema, comments_schema
from src.middlewares import validate_with_schema, \
    marshal_with_schema, dynamic_marshal_with_schema


class UserResource(Resource):
    @dynamic_marshal_with_schema(UserSchema, default_excluded=['posts'])
    def get(self, username):
        user = User.get_by_username(username)
        if not user:
            raise InvalidUsage(404, 'User not found')
        return user


class UserRegister(Resource):
    @validate_with_schema(user_schema)
    def post(self, data):
        user_in_db = User.get_by_email(data['email'])
        if user_in_db:
            raise InvalidUsage(400, 'Email already registered')

        user = User(**data)
        user.save()

        token = create_access_token(identity=user)

        return {'token': token, 'username': user.username}, 201


class UserLogin(Resource):
    @validate_with_schema(login_schema)
    @marshal_with_schema(user_schema)
    def post(self, data):
        user = User.get_by_email(data['email'])

        if not user or not user.check_hash(data['password']):
            raise InvalidUsage(403, 'Invalid credentials')

        token = create_access_token(identity=user)
        user.token = token
        return user


class UserMe(Resource):
    @jwt_required
    @validate_with_schema(user_schema, partial=True)
    @marshal_with_schema(user_schema)
    def put(self, data):
        user = current_user
        user.update(**data)
        return user

    @jwt_required
    @dynamic_marshal_with_schema(UserSchema, default_excluded=['posts'])
    def get(self):
        return current_user


class PostsResource(Resource):
    @jwt_required
    @validate_with_schema(post_schema)
    @marshal_with_schema(post_schema, status_code=201)
    def post(self, data):
        post = Post(**data, owner_id=current_user.id)
        post.save()

        return post

    @jwt_optional
    @marshal_with_schema(posts_schema, paginate=True)
    def get(self):
        POSTS_PER_PAGE = 5
        page = req.args.get('page', 1, int)

        posts = Post.\
            with_favorites().\
            paginate(page, POSTS_PER_PAGE, False)

        return posts


class PostResource(Resource):
    @marshal_with_schema(post_schema)
    def get(self, post_id):
        post = Post.get_one(post_id)
        if not post:
            raise InvalidUsage(404, 'Post not found')

        return post

    @jwt_required
    def delete(self, post_id):
        user = current_user
        post = Post.get_one(post_id)

        if not post:
            raise InvalidUsage(404, 'Post not found')
        if post.owner_id != user.id:
            raise InvalidUsage(403, 'Permission denied')

        post.delete()
        return {'deleted': post.id}

    @jwt_required
    @validate_with_schema(post_schema, partial=True)
    @marshal_with_schema(post_schema)
    def put(self, post_id, data):
        user = current_user
        post = Post.get_one(post_id)

        if not post:
            raise InvalidUsage(404, 'Post not found')
        if user.id != post.owner_id:
            raise InvalidUsage(403, 'Permission denied')

        post.update(**data)

        return post


class CommentsResource(Resource):

    @jwt_required
    @validate_with_schema(comment_schema)
    @marshal_with_schema(comment_schema, status_code=201)
    def post(self, post_id, data):
        post = Post.get_one(post_id)
        if not post:
            raise InvalidUsage(404, 'Post not found')
        comment = Comment(post.id, author_id=current_user.id, **data)
        comment.save()

        return comment

    @marshal_with_schema(comments_schema)
    def get(self, post_id):
        post = Post.get_one(post_id)
        if not post:
            raise InvalidUsage(404, 'Post not found')
        comments = post.comments

        return comments


class CommentResource(Resource):

    @jwt_required
    @validate_with_schema(comment_schema)
    @marshal_with_schema(comment_schema)
    def put(self, post_id, comment_id, data):
        post = Post.get_one(post_id)
        if not post:
            raise InvalidUsage(404, 'Post not found')
        comment = post.comments.filter_by(id=comment_id).first()
        if not comment:
            raise InvalidUsage(404, 'Comment not found')
        if comment.author_id != current_user.id:
            raise InvalidUsage(403, 'Permission denied')
        comment.update(**data)

        return comment

    @jwt_required
    def delete(self, post_id, comment_id):
        post = Post.get_one(post_id)
        if not post:
            raise InvalidUsage(404, 'Post not found')
        comment = post.comments.filter_by(id=comment_id).first()
        if not comment:
            raise InvalidUsage(404, 'Comment not found')
        if comment.author_id != current_user.id:
            raise InvalidUsage(403, 'Permission denied')
        comment.delete()

        return {'deleted': comment.id}
