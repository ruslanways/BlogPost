from django.urls import include, path
from .views import CreateLikeView, HomeView, HomeViewLikeOrdered, PostDeleteView, PostDetailView, AuthorDetailView, AuthorListView, PostListView, PostUpdateView, SignUp, Login, PasswordReset, CustomPasswordResetConfirmView, CreatePostView, getLikes
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('like_ordered/', HomeViewLikeOrdered.as_view(), name='home-like-ordering'),
    path('posts/add/', CreatePostView.as_view(), name='post-add'),
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
    path('likes/add/<pk>', CreateLikeView.as_view(), name='add-like'),
    path('posts/<pk>/update', PostUpdateView.as_view(), name='post-update'),
    path('posts/<pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('likes_count/<pk>', getLikes, name='likes_count')
]

