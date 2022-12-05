from django.test import TestCase, Client


class CoreViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_404_page_template(self):
        response = CoreViewsTest.guest_client.get('/sssssss/')
        self.assertTemplateUsed(response, 'core/404.html')
