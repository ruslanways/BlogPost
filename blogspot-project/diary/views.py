from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import Post

class HomeView(ListView):
    template_name = 'diary/index.html'
    model = Post

