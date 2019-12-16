from src.models import User
from flask import Response
import json


def user_loader(_id):
    return User.get_one(_id)


def identity_loader(user):
    return user.id


def create_response(body, status_code=200, **kwargs):
    return Response(
        response=json.dumps(body),
        status=status_code,
        content_type='application/json',
        **kwargs
    )


def success_response(body, status_code=200, **kwargs):
    return create_response(
        {'data': body},
        status_code,
        **kwargs
    )


def error_response(errors, status_code=400, **kwargs):
    return create_response(
        {'error': errors},
        status_code,
        **kwargs
    )
