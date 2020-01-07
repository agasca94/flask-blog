from flask import jsonify


class InvalidUsage(Exception):
    status_code = 500

    def __init__(self, status_code=500, message='Unknown error', payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict()
        if self.payload:
            rv['errors'] = self.payload
        rv['message'] = self.message
        return rv


def error_handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def missing_token_handler(error):
    return {
        'message': 'Request does not contain an access token.'
    }, 401


def invalid_token_handler(error):
    return {
        'message': 'Signature verification failed.'
    }, 401


def expired_token_handler(error):
    return {
        'message': 'Session expired'
    }, 401
