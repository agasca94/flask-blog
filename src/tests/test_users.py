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
        self.assertIn('token', res.json['data'])

    def test_user_creation_with_existing_email(self):
        user = User('A', 'tester@mail.com', 'pass')
        user.save()
        res = self.client.post(
            '/register',
            json=self.user
        )
        self.assertEqual(res.json, {
            'error': 'Email already registered'
        })
        self.assertEqual(res.status_code, 400)

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
        self.assertIn('token', res.json['data'])

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
            'error': 'Invalid credentials'
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


if __name__ == '__main__':
    unittest.main()
