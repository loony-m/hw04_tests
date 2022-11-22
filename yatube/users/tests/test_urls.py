from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

User = get_user_model()


class UserURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_page_status(self):
        pages = {
            'guest_client': {
                'page_ok': [
                    '/auth/signup/',
                    '/auth/login/',
                    '/auth/password_reset/',
                    '/auth/password_reset/done/',
                    '/auth/reset/done/',
                    '/auth/logout/',
                ],
                'page_redirect': [
                    '/auth/password_change/',
                    '/auth/password_change/done/',
                ]
            },
            'authorized_client': {
                'page_ok': [
                    '/auth/signup/',
                    '/auth/login/',
                    '/auth/password_reset/',
                    '/auth/password_reset/done/',
                    '/auth/reset/done/',
                    '/auth/password_change/',
                    '/auth/password_change/done/',
                    '/auth/logout/',
                ]
            }
        }

        for user_type in pages:
            for page_type in pages[user_type]:
                if page_type == 'page_ok':
                    http_status = HTTPStatus.OK.value
                else:
                    http_status = HTTPStatus.FOUND.value

                for page in pages[user_type][page_type]:
                    with self.subTest():
                        if user_type == 'guest_client':
                            response = UserURLTest.guest_client.get(page)
                        else:
                            response = UserURLTest.authorized_client.get(page)

                        self.assertEqual(response.status_code, http_status)
