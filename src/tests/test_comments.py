import unittest
from src.tests.base import AuthorizedTestCase
from src.models import Post, User, Comment


class CommentTest(AuthorizedTestCase):
    def setUp(self):
        super().setUp()
        self.post = {
            'title': 'Test Post',
            'description': 'Test description',
            'contents': 'Test contents'
        }
        self.comment = {
            'contents': 'Test Comment'
        }

    def test_comment_created(self):
        user = User(**self.user)
        user.save()
        post = Post(**self.post, owner_id=user.id)
        post.save()

        res = self.authorized_post(
            f"/posts/{post.id}/comments",
            user,
            json=self.comment,
        )

        data = res.json
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['contents'], self.comment['contents'])
        self.assertEqual(data['author']['id'], user.id)
        self.assertIn('created_at', data)

    def test_comments_retrieved(self):
        COMMENTS_NUM = 5
        user = User(**self.user)
        user.save()
        post = Post(owner_id=user.id, **self.post)
        post.save()
        [Comment(**self.comment, post_id=post.id, author_id=user.id).save()
            for _ in range(COMMENTS_NUM)]

        res = self.client.get(f"/posts/{post.id}/comments")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), COMMENTS_NUM)

    def test_comments_from_post_not_found(self):
        res = self.client.get('/posts/1/comments')

        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json['message'], 'Post not found')

    def test_comment_updated(self):
        new_data = {
            'contents': 'New contents'
        }
        user = User(**self.user)
        user.save()
        post = Post(owner_id=user.id, **self.post)
        post.save()
        comment = Comment(**self.comment, post_id=post.id, author_id=user.id)
        comment.save()

        res = self.authorized_put(
            f"/posts/{post.id}/comments/{comment.id}",
            user,
            json=new_data
        )

        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['contents'], new_data['contents'])
        self.assertEqual(data['author']['id'], user.id)

    def test_comment_unauthorized_update(self):
        new_data = {
            'contents': 'New contents'
        }
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()
        post = Post(**self.post, owner_id=user.id)
        post.save()
        comment = Comment(**self.comment, post_id=post.id, author_id=user.id)
        comment.save()

        res = self.authorized_put(
            f"/posts/{post.id}/comments/{comment.id}",
            user2,
            json=new_data
        )

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json['message'], 'Permission denied')

    def test_comment_deleted(self):
        user = User(**self.user)
        user.save()
        post = Post(**self.post, owner_id=user.id)
        post.save()
        comment = Comment(**self.comment, post_id=post.id, author_id=user.id)
        comment.save()

        res = self.authorized_delete(
            f"/posts/{post.id}/comments/{comment.id}",
            user
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['deleted'], comment.id)

    def test_comment_unauthorized_delete(self):
        user = User(**self.user)
        user.save()
        user2 = User('Another', 'another', 'another@mail.com', 'secret')
        user2.save()

        post = Post(**self.post, owner_id=user.id)
        post.save()
        comment = Comment(**self.comment, post_id=post.id, author_id=user.id)
        comment.save()

        res = self.authorized_delete(f"/posts/{post.id}", user2)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json['message'], 'Permission denied')


if __name__ == '__main__':
    unittest.main()
