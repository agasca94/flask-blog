from flask import request
from marshmallow import ValidationError
from functools import wraps


def validate_with_schema(schema, **kwargs):
    def decorator(func):
        @wraps(func)
        def inner(self):
            # Deserialize and validate incoming data
            req_data = request.get_json()

            try:
                data = schema.load(req_data, **kwargs)
            except ValidationError as err:
                return {'error': err.messages}

            return func(self, data)
        return inner
    return decorator


def marshal_with_schema(schema):
    def decorator(func):
        @wraps(func)
        def inner(*data, **kwargs):
            data = func(*data, **kwargs)
            return schema.dump(data)
        return inner
    return decorator
