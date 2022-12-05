from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


from posts.models import Post, Comment

User = get_user_model()


class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test')
        cls.user_no_have_post = User.objects.create(username='test_2')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_nohave_post = Client()
        cls.authorized_client_nohave_post.force_login(cls.user_no_have_post)

        cls.post = Post.objects.create(
            text='Новый пост',
            author=cls.user
        )

    def test_add_post_authorized_client(self):
        post_count = Post.objects.count()

        form_field = {
            'text': 'Новый пост 2',
            'author': FormTest.authorized_client
        }

        FormTest.authorized_client.post(
            reverse('posts:post_create'),
            data=form_field,
            follow=True
        )

        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_add_post_guest_client(self):
        form_field = {
            'text': 'Новый пост 3',
            'author': FormTest.guest_client
        }

        before_post_count = Post.objects.count()

        FormTest.guest_client.post(
            reverse('posts:post_create'),
            data=form_field,
            follow=True
        )

        after_post_count = Post.objects.count()

        self.assertEqual(before_post_count, after_post_count)

    def test_edit_post_authorized_client(self):
        form_edited_field = {
            'text': 'Новый пост 3',
            'author': FormTest.authorized_client
        }

        FormTest.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': FormTest.post.id}),
            data=form_edited_field,
            follow=True
        )

        post_edited = Post.objects.get(id=FormTest.post.id)

        self.assertEqual(post_edited.text, form_edited_field['text'])

    def test_edit_post_guest_client(self):
        response = FormTest.guest_client.get('/posts/1/edit/')

        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_edit_no_have_post_authorized_client(self):
        response = FormTest.authorized_client_nohave_post.get('/posts/1/edit/')

        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_add_comment_guest_client(self):

        response = FormTest.authorized_client_nohave_post.get(f'/posts/{FormTest.post.id}/comment/')

        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_availiable_comment(self):
        form_field = {
            'text': 'Тестовый комментарий',
            'author': FormTest.authorized_client,
            'post': FormTest.post
        }

        FormTest.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': FormTest.post.id}),
            data=form_field,
            follow=True
        )

        after_comment_count = Comment.objects.filter(
            post=FormTest.post
        ).count()

        self.assertEqual(after_comment_count, 1)
