from django.urls import path
from .views import HomeView, PostDetailView, AuthorDetailView, AuthorListView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('posts/<pk>/', PostDetailView.as_view(), name='post-detail'),
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('authors/<pk>/', AuthorDetailView.as_view(), name='author-detail'),
]
