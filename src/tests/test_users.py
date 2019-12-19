import unittest
from src.tests.base import BaseTestCase, AuthorizedTestCase
from src.models import User


class AuthTest(BaseTestCase):
    def test_user_creation(self):
        res = self.client.post(
            '/register',
            json=self.user
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json)

    def test_user_creation_with_existing_email(self):
        user = User('A', 'tester@mail.com', 'pass')
        user.save()
        res = self.client.post(
            '/register',
            json=self.user
        )
        self.assertEqual(res.json, {
            'message': 'Email already registered'
        })
        self.assertEqual(res.status_code, 400)

    def test_user_creation_with_invalid_data(self):
        new_data = {
            'name': 123,
            'email': 'notamail'
        }
        res = self.client.post(
            '/register',
            json=new_data
        )

        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.json['errors'], {
            'email': ['Not a valid email address.'],
            'name': ['Not a valid string.'],
            'password': ['Missing data for required field.']
        })
        self.assertEqual(res.json['message'], 'Invalid data')

    def test_user_login(self):
        user = User(**self.user)
        user.save()
        credentials = {
            'email': self.user['email'],
            'password': self.user['password']
        }
        res = self.client.post(
            '/login',
            json=credentials
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('token', res.json)

    def test_user_login_with_wrong_credentials(self):
        credentials = {
            'email': 'something@mail.com',
            'password': 'wrongpass'
        }
        res = self.client.post(
            '/login',
            json=credentials
        )
        self.assertEqual(res.json, {
            'message': 'Invalid credentials'
        })


class UserTest(AuthorizedTestCase):
    def test_user_get_me(self):
        user = User(**self.user)
        user.save()
        res = self.authorized_get(
            '/me',
            user
        )
        self.assertEqual(res.json, {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'posts': user.posts,
        })

    def test_user_not_authenticated(self):
        res = self.client.get('/me')
        self.assertEqual(res.status_code, 403)
        self.assertEqual(
            res.json['message'],
            'Request does not contain an access token.'
        )

    def test_user_with_invlid_token(self):
        res = self.client.get(
            '/me',
            headers={'Authorization': 'Bearer badtoken'}
        )
        self.assertEqual(res.status_code, 403)
        self.assertEqual(
            res.json['message'],
            'Signature verification failed.'
        )


if __name__ == '__main__':
    unittest.main()
