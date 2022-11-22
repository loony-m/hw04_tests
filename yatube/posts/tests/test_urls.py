from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post_authorized = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )

        cls.group = Group.objects.create(
            title='Тест группа',
            slug='test_group'
        )

    def test_pages_available_for_guest_users(self):
        pages = ['/', '/group/test_group/', '/profile/test/', '/posts/1/']

        for page in pages:
            with self.subTest():
                response = StaticURLTests.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_page_with_redirect_for_guest_user(self):
        pages = ['/posts/1/edit/', '/create/']

        for page in pages:
            with self.subTest():
                response = StaticURLTests.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_page_with_redirect_for_authorized_user(self):
        pages = ['/posts/1/edit/', '/create/']

        for page in pages:
            with self.subTest():
                response = StaticURLTests.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_page_404(self):
        response_authorized = StaticURLTests.authorized_client.get(
            '/aaaaaaaaaaaaa/')
        self.assertEqual(
            response_authorized.status_code,
            HTTPStatus.NOT_FOUND.value
        )

        response_guest = StaticURLTests.guest_client.get(
            '/aaaaaaaaaaaaa/')
        self.assertEqual(
            response_guest.status_code,
            HTTPStatus.NOT_FOUND.value
        )

    def test_templates_for_guest_user(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_group/',
            'posts/profile.html': '/profile/test/',
            'posts/post_detail.html': '/posts/1/',
        }

        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_templates_for_authorized_user(self):
        templates_url_names = {
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
