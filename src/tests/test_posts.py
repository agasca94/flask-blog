import unittest
from src.tests.base import AuthorizedTestCase
from src.models import Post, User


class PostTest(AuthorizedTestCase):
    def setUp(self):
        super().setUp()
        self.post = {
            'title': 'Test Post',
            'contents': 'Test contents'
        }

    def test_post_created(self):
        user = User(**self.user)
        user.save()

        res = self.authorized_post(
            '/posts',
            user,
            json=self.post,
        )

        data = res.json
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['title'], self.post['title'])
        self.assertEqual(data['contents'], self.post['contents'])
        self.assertEqual(data['author']['id'], user.id)

    def test_post_retrieved(self):
        user = User(**self.user)
        user.save()
        post = Post(**self.post, owner_id=user.id)
        post.save()

        res = self.client.get(f"/posts/{post.id}")

        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['title'], self.post['title'])
        self.assertEqual(data['contents'], self.post['contents'])
        self.assertEqual(data['author']['id'], user.id)

    def test_post_not_found(self):
        res = self.client.get(f"/posts/1")

        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json['message'], 'Post not found')

    def test_post_updated(self):
        new_data = {
            'title': 'New title',
            'contents': 'New contents'
        }
        user = User(**self.user)
        user.save()
        post = Post(**self.post, owner_id=user.id)
        post.save()

        res = self.authorized_put(f"/posts/{post.id}", user, json=new_data)

        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['title'], new_data['title'])
        self.assertEqual(data['contents'], new_data['contents'])
        self.assertEqual(data['author']['id'], user.id)

    def test_post_unauthorized_update(self):
        new_data = {
            'title': 'New title',
            'contents': 'New contents'
        }
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()
        post = Post(**self.post, owner_id=user.id)
        post.save()

        res = self.authorized_put(f"/posts/{post.id}", user2, json=new_data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json['message'], 'Permission denied')

    def test_post_deleted(self):
        user = User(**self.user)
        user.save()
        post = Post(**self.post, owner_id=user.id)
        post.save()

        res = self.authorized_delete(f"/posts/{post.id}", user)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['deleted'], post.id)

    def test_post_unauthorized_delete(self):
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()

        post = Post(**self.post, owner_id=user.id)
        post.save()

        res = self.authorized_delete(f"/posts/{post.id}", user2)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json['message'], 'Permission denied')


if __name__ == '__main__':
    unittest.main()
