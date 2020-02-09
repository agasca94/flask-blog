import unittest
from src.tests.base import AuthorizedTestCase
from src.models import Post, User


class TagsTest(AuthorizedTestCase):
    def setUp(self):
        super().setUp()
        self.post = {
            'title': 'Test Post',
            'description': 'Test description',
            'contents': 'Test contents'
        }

    def test_post_created(self):
        user = User(**self.user)
        user.save()
        post = Post(**self.post, owner_id=user.id, tags=['java', 'python'])
        post.save()

        post = Post(**self.post, owner_id=user.id, tags=['ruby', 'python'])
        post.save()

        post = Post(**self.post, owner_id=user.id, tags=['aws', 'azure'])
        post.save()

        post = Post(**self.post, owner_id=user.id, tags=['python', 'aws'])
        post.save()

        post = Post(**self.post, owner_id=user.id, tags=['java', 'ml'])
        post.save()

        res = self.client.get('/tags')
        self.assertEqual(res.json, [
            'python',
            'aws',
            'java',
            'azure',
            'ml',
            'ruby',
        ])


if __name__ == '__main__':
    unittest.main()
