from django.views.generic import ListView, DetailView
from .models import Post, CustomUser
from django.db.models import Count, Prefetch

class HomeView(ListView):
    template_name = 'diary/index.html'
    queryset = Post.objects.annotate(Count('like')).select_related('author').filter(published=True)
    ordering = ['-like__count']


class PostListView(ListView):
    queryset = Post.objects.annotate(Count('like')).select_related('author')


class PostDetailView(DetailView):
    queryset = Post.objects.annotate(Count('like')).select_related('author')


class AuthorListView(ListView):
    model = CustomUser


class AuthorDetailView(DetailView):
    queryset = CustomUser.objects.all().prefetch_related(Prefetch('post_set', queryset=Post.objects.annotate(Count('like')).order_by('-like__count', '-updated')))


