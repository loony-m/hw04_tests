from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


User = get_user_model()


class UserTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

    def test_add_user(self):
        form_field = {
            'first_name': 'Сергей',
            'last_name': 'Сергеев',
            'username': 'sergey',
            'email': 'sergey@ya.ru',
            'password1': '1q2w3e!@#',
            'password2': '1q2w3e!@#',
        }

        UserTest.guest_client.post(
            reverse('users:signup'),
            data=form_field,
            follow=True
        )

        user = User.objects.get(username=form_field['username'])

        self.assertEqual(form_field['username'], user.username)
