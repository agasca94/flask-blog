from marshmallow import Schema, fields, post_dump


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


class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    contents = fields.Str(required=True)
    author = fields.Nested(UserSchema(exclude=('posts',)))
    created_at = fields.DateTime(dump_only=True)


def get_pagination_schema(schema):
    class PaginationSchema(Schema):
        page = fields.Int(dump_only=True)
        pages = fields.Int(dump_only=True)
        next_num = fields.Int(dump_only=True)
        prev_num = fields.Int(dump_only=True)
        total = fields.Int(dump_only=True)
        items = fields.Nested(schema, many=True)

        @post_dump
        def dump_pagination(self, data, **kwargs):
            items = data.pop('items', [])
            return {
                'meta': data,
                'data': items
            }

    return PaginationSchema()


login_schema = LoginSchema()

user_schema = UserSchema(exclude=('posts',))

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
