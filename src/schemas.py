from marshmallow import fields, Schema


class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
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
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
    posts = fields.Nested(PostSchema(exclude=('author',)), many=True)


user_schema = UserSchema()
login_schema = LoginSchema()
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
