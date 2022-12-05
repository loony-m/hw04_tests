from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {'text': 'Введите описание', 'group': 'Укажите группу'}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
