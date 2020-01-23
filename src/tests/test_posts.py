import unittest
from src.tests.base import AuthorizedTestCase
from src.models import Post, User


class PostTest(AuthorizedTestCase):
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

        res = self.authorized_post(
            '/posts',
            user,
            json=self.post,
        )

        data = res.json
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['title'], self.post['title'])
        self.assertEqual(data['description'], self.post['description'])
        self.assertEqual(data['contents'], self.post['contents'])
        self.assertEqual(data['author']['id'], user.id)

    def test_post_retrieved(self):
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()
        post = Post(**self.post, owner_id=user.id)
        post.favorited_by = [user, user2]
        post.save()

        res = self.client.get(f"/posts/{post.id}")

        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['title'], self.post['title'])
        self.assertEqual(data['description'], self.post['description'])
        self.assertEqual(data['contents'], self.post['contents'])
        self.assertEqual(data['author']['id'], user.id)
        self.assertEqual(data['favorites_count'], 2)
        self.assertEqual(data['is_favorited'], False)

    def test_posts_retrieved(self):
        POSTS_NUM = 11
        POSTS_PER_PAGE = 5
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()

        posts = [Post(**self.post, owner_id=user.id) for _ in range(POSTS_NUM)]
        posts[0].favorited_by = [user, user2]
        posts[1].favorited_by = [user]
        posts[2].favorited_by = [user2]
        [post.save() for post in posts]

        res = self.authorized_get(
            '/posts',
            user
        )

        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['data']), POSTS_PER_PAGE)
        self.assertEqual(data['meta']['total'], POSTS_NUM)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['next_num'], 2)

        data = data['data']
        favorites = {
            'is_favorited': [
                post['is_favorited'] for post in data
            ],
            'favorites_count': [
                post['favorites_count'] for post in data
            ],
        }
        self.assertEqual(favorites, {
            'is_favorited': [True, True, False] + [False]*2,
            'favorites_count': [2, 1, 1] + [0]*2
        })

    def test_post_not_found(self):
        res = self.client.get(f"/posts/1")

        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json['message'], 'Post not found')

    def test_post_updated(self):
        new_data = {
            'title': 'New title',
            # 'description': 'Not updated'
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
        # Assert that description remains unchanged
        self.assertEqual(data['description'], self.post['description'])

    def test_post_unauthorized_update(self):
        new_data = {
            'title': 'New title',
            'description': 'New description',
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
