from multiprocessing import context
from pyexpat import model
from urllib import request
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Post, CustomUser
from django.db.models import Count

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
    queryset = CustomUser.objects.all().prefetch_related('post_set')
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['likes'] = Post.objects.annotate(Count('like')).filter(author__pk=self.object.pk).select_related('author')
    #     return context

