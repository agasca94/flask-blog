from marshmallow import fields, Schema


class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    contents = fields.Str(required=True)
    author = fields.Nested(lambda: UserSchema(exclude=('posts',)))
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class LoginSchema(Schema):
    email = fields.Email(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    username = fields.Str(required=True)
    bio = fields.Str(required=False)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    token = fields.Str(dump_only=True)
    posts = fields.Nested(PostSchema(exclude=('author',)), many=True)


user_schema = UserSchema(exclude=('posts',))
login_schema = LoginSchema()
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
