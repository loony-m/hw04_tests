from django.test import TestCase, Client
from http import HTTPStatus


class AboutUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_user = Client()

    def test_page_status(self):
        pages = ['/about/author/', '/about/tech/']

        for page in pages:
            with self.subTest():
                response = AboutUrlTest.guest_user.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
