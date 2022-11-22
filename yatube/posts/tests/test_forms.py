from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


from posts.models import Post

User = get_user_model()


class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(
            text='Новый пост',
            author=cls.user
        )

    def test_add_post(self):
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

    def test_edit_post(self):
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
