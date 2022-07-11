from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import Post
from django.db.models import Count

class HomeView(ListView):
    template_name = 'diary/index.html'
    queryset = Post.objects.annotate(Count('like'))
    ordering = ['-like__count']

