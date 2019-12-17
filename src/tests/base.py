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
            'email': 'tester@mail.com',
            'password': 'secret'
        }

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class AuthorizedTestCase(BaseTestCase):
    def authorized_get(self, url, user, body={}, headers={}, **kwargs):
        token = create_access_token(identity=user)
        headers.update({
            'Authorization': f"Bearer {token}"
        })
        return self.client.get(
            url,
            query_string=body,
            headers=headers,
            **kwargs
        )
