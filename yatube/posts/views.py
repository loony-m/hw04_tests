from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

POST_COUNT = 10


def get_pagination(request, elements, count_on_page):
    paginator = Paginator(elements, count_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    result = {'elements': page_obj, 'elements_count': paginator.count}

    return result


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.select_related('group')
    page_obj = get_pagination(request, posts, POST_COUNT)

    context = {
        'title': title,
        'page_obj': page_obj['elements'],
    }

    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    title = group.title

    posts = group.posts.all()
    page_obj = get_pagination(request, posts, POST_COUNT)

    context = {
        'title': title,
        'page_obj': page_obj['elements'],
        'group': group,
    }

    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user.id).all()
    page_obj = get_pagination(request, posts, POST_COUNT)

    context = {
        'page_obj': page_obj['elements'],
        'posts_count': page_obj['elements_count'],
        'title': f'Профайл пользователя {user.username}',
        'author': user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = User.objects.get(username=post.author)
    post_count = Post.objects.filter(author=user.id).count()

    context = {
        'username': post.author,
        'author_post_count': post_count,
        'post': post,
        'title': 'Пост ' + post.text[0:30],
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form_post = form.save(commit=False)
            author = get_object_or_404(User, username=request.user.username)
            form_post.author = author
            form_post.save()
            return redirect(f'/profile/{request.user.username}/')
    else:
        form = PostForm()

    context = {
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if not post.author.id == request.user.id:
        return redirect(f'/posts/{post_id}/')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}/')
    else:
        form = PostForm(instance=post)

    context = {
        'is_edit': True,
        'form': form,
        'post_id': post_id,
    }
    return render(request, 'posts/create_post.html', context)
