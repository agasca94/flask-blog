from flask import request, Response
from marshmallow import ValidationError
from functools import wraps
from src.exceptions import InvalidUsage


def validate_with_schema(schema, error_msg='Invalid data', **kwargs):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kkwargs):
            # Deserialize and validate incoming data
            req_data = request.get_json()

            try:
                data = schema.load(req_data, **kwargs)
            except ValidationError as err:
                raise InvalidUsage(422, error_msg, err.messages)
            kkwargs['data'] = data
            return func(*args, **kkwargs)
        return inner
    return decorator


def _dumped_data(data, schema):
    # Return any custom response (commonly an error) as is,
    # without parsing it
    if isinstance(data, dict) or isinstance(data, Response):
        return data
    try:
        d, *rest = data
        return schema.dump(d), *rest
    except TypeError:
        return schema.dump(data)


def marshal_with_schema(schema):
    def decorator(func):
        @wraps(func)
        def inner(*data, **kwargs):
            data = func(*data, **kwargs)

            return _dumped_data(data, schema)
        return inner
    return decorator


def dynamic_marshal_with_schema(schema_cls, default_excluded=[]):
    def decorator(func):
        @wraps(func)
        def inner(*data, **kwargs):
            include_fields = request.args.getlist('include')
            excluded = set(
                default_excluded
            ).symmetric_difference(set(
                include_fields
            ))

            data = func(*data, **kwargs)
            many = isinstance(data, list)
            schema = schema_cls(exclude=excluded, many=many)

            return _dumped_data(data, schema)
        return inner
    return decorator
