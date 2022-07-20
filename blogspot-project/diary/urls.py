from django.urls import include, path
from .views import HomeView, PostDetailView, AuthorDetailView, AuthorListView, PostListView, SignUp, Login, PasswordReset, CustomPasswordResetConfirmView, CreatePostView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<pk>/', PostDetailView.as_view(), name='post-detail'),
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('authors/<sortfield>', AuthorListView.as_view(), name='author-list'),
    path('authors/<pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('signup/', SignUp.as_view(), name='signup'),
    path('login/', Login.as_view(), name="login"),
    path('password_reset/', PasswordReset.as_view(), name="password_reset"),
    path(
        'reset/<uidb64>/<token>/',
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm"
    ),
    path('', include('django.contrib.auth.urls')),
    path('posts/add', CreatePostView.as_view(), name='post-add')
]

