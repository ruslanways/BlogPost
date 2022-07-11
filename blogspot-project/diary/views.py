from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import Post
from django.db.models import Count

class HomeView(ListView):
    template_name = 'diary/index.html'
    queryset = Post.objects.annotate(Count('like')).select_related('author')
    ordering = ['-like__count']

