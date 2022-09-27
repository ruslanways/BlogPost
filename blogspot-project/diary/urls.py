import imp
from urllib import request
from django.urls import include, path
from .views import CreateLikeAPIView, CreateLikeView, HomeView, HomeViewLikeOrdered, LikeAPIView, LikeAnalytics, LikeDetailAPIView, MyTokenObtainPairView, PostAPIDetailView, PostCreateAPIView, PostDeleteView, PostDetailView, AuthorDetailView, AuthorListView, PostListView, PostUpdateView, PostsAPIView, SignUp, Login, PasswordReset, CustomPasswordResetConfirmView, CreatePostView, UserDetailAPIView, UserListAPIView, getLikes
from django.contrib.auth.views import LogoutView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



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
    path('likes_count/<pk>', getLikes, name='likes_count'),


    path('api/v1/users/', UserListAPIView.as_view(), name='users-list-create-api'),
    path('api/v1/users/<int:pk>', UserDetailAPIView.as_view(), name='user-detail-update-destroy-api'),

    path('api/v1/postslist/', PostsAPIView.as_view(), name='post-list-api'),
    path('api/v1/postcreate/', PostCreateAPIView.as_view()),
    path('api/v1/postdetail/<int:pk>', PostAPIDetailView.as_view(), name='post-detail-api'),

    path('api/v1/createlike/<int:pk>', CreateLikeAPIView.as_view()),
    path('api/v1/analytics/', LikeAnalytics.as_view()),
    path('api/v1/likelist/', LikeAPIView.as_view(), name='like-list-api'),
    path('api/v1/likedetail/<int:pk>', LikeDetailAPIView.as_view(), name='like-detail-api'),

    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

