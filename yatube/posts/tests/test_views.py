import shutil
import tempfile


from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile


from posts.models import Post, Group, Follow
from posts.forms import PostForm


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_user = Client()
        cls.authorized_user = Client()
        cls.user = User.objects.create_user(username='test')
        cls.authorized_user.force_login(cls.user)

        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.image,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.group_empty = Group.objects.create(
            title='Тестовая пустая группа',
            slug='test_group_empty',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_templates(self):
        cache.clear()

        templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:group_posts', kwargs={'slug': 'test_group'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'test'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': PostsViewsTest.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostsViewsTest.post.id}
            ): 'posts/create_post.html',
        }

        for reverse_name, template in templates.items():
            with self.subTest(template=template):
                response = PostsViewsTest.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_page_index(self):
        cache.clear()

        response = PostsViewsTest.guest_user.get(reverse('posts:index'))

        self.assertEqual(
            response.context.get('page_obj').object_list[0].image,
            'posts/small.gif'
        )

        self.assertIsInstance(
            list(response.context.get('page_obj').object_list),
            list
        )

    def test_context_page_create(self):
        response = PostsViewsTest.authorized_user.get(
            reverse('posts:post_create')
        )

        self.assertIsInstance(
            response.context.get('form'),
            PostForm
        )

    def test_context_page_group(self):
        response = PostsViewsTest.authorized_user.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': PostsViewsTest.group.slug}
            )
        )

        self.assertEqual(
            response.context.get('page_obj').object_list[0].image,
            'posts/small.gif'
        )

        self.assertIsInstance(
            response.context.get('page_obj').object_list,
            list
        )

    def test_context_page_profile(self):
        response = PostsViewsTest.authorized_user.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTest.user.username}
            )
        )

        self.assertEqual(
            response.context.get('page_obj').object_list[0].image,
            'posts/small.gif'
        )

        self.assertIsInstance(
            response.context.get('page_obj').object_list,
            list
        )

    def test_context_page_post_detail(self):
        response = PostsViewsTest.authorized_user.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewsTest.post.id}
            )
        )

        self.assertEqual(
            response.context.get('post').image,
            'posts/small.gif'
        )

        self.assertEqual(
            response.context.get('post').text,
            'Тестовый заголовок'
        )

    def test_availiable_post_on_page(self):
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_posts',
                kwargs={'slug': PostsViewsTest.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTest.user.username}
            )
        ]

        for page in pages:
            with self.subTest():
                response = PostsViewsTest.authorized_user.get(page)
                post = response.context['page_obj'][0]
                self.assertEqual(
                    post.text,
                    PostsViewsTest.post.text
                )

    def test_no_availiable_post_on_page(self):
        response = PostsViewsTest.authorized_user.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': PostsViewsTest.group_empty.slug}
            )
        )

        self.assertEqual(
            len(response.context['page_obj'].object_list),
            0
        )

    def test_availiable_post_with_image(self):
        post = Post.objects.filter(pk=PostsViewsTest.post.id)

        self.assertIsNotNone(post)

    def test_cache(self):
        cache.set('test', 'hello', 20)
        self.assertEqual(cache.get('test'), 'hello')


class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_user = Client()
        cls.user = User.objects.create_user(username='test_2')
        cls.authorized_user.force_login(cls.user)
        cls.count_page = 10
        cls.posts = []

        cls.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_group_2',
            description='Тестовое описание 2',
        )

        for i in range(1, 13):
            cls.posts.append(
                Post.objects.create(
                    text=f'Тестовый заголовок - {i}',
                    author=cls.user,
                    group=cls.group,
                )
            )

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_paginator_of_index_page(self):
        response = PostPaginatorTest.authorized_user.get(
            reverse('posts:index')
        )

        self.assertEqual(
            len(response.context['page_obj']),
            PostPaginatorTest.count_page
        )

    def test_paginator_of_group_page(self):
        response = PostPaginatorTest.authorized_user.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': PostPaginatorTest.group.slug}
            )
        )

        self.assertTrue(
            response.context['page_obj'].has_other_pages
        )

    def test_paginator_of_profile_page(self):
        response = PostPaginatorTest.authorized_user.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPaginatorTest.user.username}
            )
        )

        self.assertTrue(
            response.context['page_obj'].has_other_pages
        )


class PostFollowerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        cls.user_author = User.objects.create_user(username='test_author')
        cls.author = Client()
        cls.author.force_login(cls.user_author)

        cls.group = Group.objects.create(
            title='Тестовая группа 3',
            slug='test_group_3',
            description='Тестовое описание 3',
        )

        cls.post = Post.objects.create(
            text='Тестовый заголовок 3',
            author=cls.user_author,
            group=cls.group,
        )

        cls.subscribe = Follow.objects.create(
            user=PostFollowerTest.user,
            author=PostFollowerTest.user_author
        )

    def test_user_can_follow(self):
        PostFollowerTest.authorized_user.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostFollowerTest.user_author.username}
            )
        )

        follow_count = Follow.objects.all().count()

        self.assertEqual(follow_count, 2)

    def test_user_can_unfollow(self):
        Follow.objects.create(
            user=PostFollowerTest.user,
            author=PostFollowerTest.user_author
        )

        PostFollowerTest.authorized_user.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostFollowerTest.user_author.username}
            )
        )

        after_follower_count = Follow.objects.all().count()

        self.assertEqual(after_follower_count, 0)

    def test_user_have_or_nohave_new_post(self):
        user = User.objects.create_user(username='test_user_2')
        other_authorized_user = Client()
        other_authorized_user.force_login(user)

        before_response = PostFollowerTest.authorized_user.get(
            reverse('posts:follow_index')
        )
        before_post_count = len(before_response.context['page_obj'])

        before_other_user_response = other_authorized_user.get(
            reverse('posts:follow_index')
        )
        before_other_user_post_count = len(
            before_other_user_response.context['page_obj']
        )

        Post.objects.create(
            text='Тестовый заголовок 4',
            author=PostFollowerTest.user_author,
            group=PostFollowerTest.group,
        )

        after_response = PostFollowerTest.authorized_user.get(
            reverse('posts:follow_index')
        )
        after_post_count = len(after_response.context['page_obj'])

        after_other_user_response = other_authorized_user.get(
            reverse('posts:follow_index')
        )
        after_other_user_post_count = len(
            after_other_user_response.context['page_obj']
        )

        self.assertEqual(after_post_count, before_post_count + 1)
        self.assertEqual(
            before_other_user_post_count,
            after_other_user_post_count
        )
