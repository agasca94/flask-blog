from flask import request, Response
from marshmallow import ValidationError
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request_optional
from src.exceptions import InvalidUsage
from src.schemas import get_pagination_schema


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
    return schema.dump(data)


def marshal_with_schema(schema, status_code=200, paginate=False):
    def decorator(func):
        @wraps(func)
        def inner(*data, **kwargs):
            data = func(*data, **kwargs)

            pag_schema = get_pagination_schema(schema) if paginate else schema

            return _dumped_data(data, pag_schema), status_code
        return inner
    return decorator


def dynamic_marshal_with_schema(
    schema_cls,
    default_excluded=[],
    status_code=200,
    paginate=False
):
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
            many = isinstance(data, list) or paginate
            schema = schema_cls(exclude=excluded, many=many)

            if paginate:
                schema = get_pagination_schema(schema)

            return _dumped_data(data, schema), status_code
        return inner
    return decorator


def valid_jwt_optional(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            verify_jwt_in_request_optional()
        except Exception:
            pass  # Ignore if the request contains an invalid or expired token
        return fn(*args, **kwargs)
    return inner
