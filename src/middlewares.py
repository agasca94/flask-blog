from flask import request, Response
from marshmallow import ValidationError
from functools import wraps
from src.exceptions import InvalidUsage


def validate_with_schema(schema, **kwargs):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kkwargs):
            # Deserialize and validate incoming data
            req_data = request.get_json()

            try:
                data = schema.load(req_data, **kwargs)
            except ValidationError as err:
                raise InvalidUsage(422, 'Invalid data', err.messages)
            kkwargs['data'] = data
            return func(*args, **kkwargs)
        return inner
    return decorator


def marshal_with_schema(schema):
    def decorator(func):
        @wraps(func)
        def inner(*data, **kwargs):
            data = func(*data, **kwargs)
            """
            Return any custom response (commonly an error) as is,
            without parsing it
            """
            if isinstance(data, dict) or isinstance(data, Response):
                return data
            try:
                d, *rest = data
                return schema.dump(d), *rest
            except TypeError:
                return schema.dump(data)
        return inner
    return decorator
