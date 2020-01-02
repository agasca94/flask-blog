from flask_testing import TestCase
from flask_jwt_extended import create_access_token
from src.app import create_app, db


class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app('testing')
        return app

    def setUp(self):
        self.user = {
            'name': 'Tester',
            'username': 'tester',
            'email': 'tester@mail.com',
            'password': 'secret',
            'bio': 'About me'
        }

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class AuthorizedTestCase(BaseTestCase):
    def authorized_request(self, method, url, user, **kwargs):
        token = create_access_token(identity=user)
        auth_header = {'Authorization': f"Bearer {token}"}
        kwargs['headers'] = {
            **kwargs.get('headers', {}),
            **auth_header
        }
        return getattr(self.client, method)(url, **kwargs)

    def authorized_get(self, *args, **kwargs):
        return self.authorized_request('get', *args, **kwargs)

    def authorized_post(self, *args, **kwargs):
        return self.authorized_request('post', *args, **kwargs)

    def authorized_delete(self, *args, **kwargs):
        return self.authorized_request('delete', *args, **kwargs)

    def authorized_put(self, *args, **kwargs):
        return self.authorized_request('put', *args, **kwargs)
