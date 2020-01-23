from flask import request, Response
from marshmallow import ValidationError
from functools import wraps
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


def log_sqlalchemy(func):
    @wraps(func)
    def inner(*data, **kwargs):
        import logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        res = func(*data, **kwargs)
        logging.disable()

        return res
    return inner
