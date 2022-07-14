from django.urls import include, path
from .views import HomeView, PostDetailView, AuthorDetailView, AuthorListView, PostListView, SignUp

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<pk>/', PostDetailView.as_view(), name='post-detail'),
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('authors/<pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('', include('django.contrib.auth.urls')),
    path('signup', SignUp.as_view(), name='signup'),
]

