import unittest
from src.tests.base import AuthorizedTestCase
from src.models import Post, User
from datetime import datetime as dt


class PostTest(AuthorizedTestCase):
    def setUp(self):
        super().setUp()
        self.post = {
            'title': 'Test Post',
            'description': 'Test description',
            'contents': 'Test contents',
            'tags': ['js', 'python']
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
        self.assertEqual(data['tags'], self.post['tags'])

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
        POSTS_PER_PAGE = 6
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()

        posts = [
            Post(**self.post, owner_id=user.id, created_at=dt.now())
            for _ in range(POSTS_NUM)
        ]
        posts[-1].favorited_by = [user, user2]
        posts[-2].favorited_by = [user]
        posts[-3].favorited_by = [user2]
        [post.save() for post in posts]

        res = self.authorized_get('/posts', user)

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
            'is_favorited': [True, True, False] + [False]*3,
            'favorites_count': [2, 1, 1] + [0]*3
        })

    def test_tagged_posts_retrieved(self):
        user = User(**self.user)
        user.save()
        post = Post(**self.post, owner_id=user.id)
        post.tags = ['aws']
        post.save()
        post = Post(**self.post, owner_id=user.id)
        post.tags = ['aws', 'python']
        post.save()
        post = Post(**self.post, owner_id=user.id)
        post.tags = ['azure']
        post.save()
        post = Post(**self.post, owner_id=user.id)
        post.tags = ['js', 'ruby']
        post.save()

        res = self.client.get('/posts?tag=aws')

        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['data']), 2)

    def test_posts_by_user_retrieved(self):
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()

        post1 = Post(**self.post, owner_id=user.id)
        post1.save()
        post2 = Post(**self.post, owner_id=user2.id)
        post2.save()
        post3 = Post(**self.post, owner_id=user.id)
        post3.save()
        post5 = Post(**self.post, owner_id=user2.id)
        post5.save()

        res = self.client.get(f'/@{user.username}/posts')

        data = res.json
        authors = [post['author']['id'] for post in data]
        posts_ids = [post['id'] for post in data]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(authors, [user.id]*2)
        self.assertEqual(posts_ids, [post3.id, post1.id])

    def test_favorites_retrieved(self):
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()

        post1 = Post(**self.post, owner_id=user.id)
        post1.favorited_by = [user, user2]
        post1.save()
        post2 = Post(**self.post, owner_id=user.id)
        post2.favorited_by = [user2]
        post2.save()
        post3 = Post(**self.post, owner_id=user.id)
        post3.favorited_by = [user]
        post3.save()
        post5 = Post(**self.post, owner_id=user.id)
        post5.save()

        res = self.client.get(f'/@{user.username}/favorites')

        data = res.json
        authors = [post['author']['id'] for post in data]
        posts_ids = [post['id'] for post in data]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(authors, [user.id]*2)
        self.assertEqual(posts_ids, [post3.id, post1.id])

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

    def test_post_favorited(self):
        user = User(**self.user)
        user.save()

        post = Post(**self.post, owner_id=user.id)
        post.save()

        res = self.authorized_post(
            f"/posts/{post.id}/favorite",
            user
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['favorites_count'], 1)
        self.assertEqual(res.json['is_favorited'], True)

    def test_post_unfavorited(self):
        user = User(**self.user)
        user.save()

        post = Post(**self.post, owner_id=user.id)
        post.favorited_by = [user]
        post.save()

        res = self.authorized_delete(
            f"/posts/{post.id}/favorite",
            user
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['favorites_count'], 0)
        self.assertEqual(res.json['is_favorited'], False)


if __name__ == '__main__':
    unittest.main()
