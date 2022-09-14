from dataclasses import fields
from email.policy import default
from rest_framework import serializers
from .models import CustomUser, Like, Post


class PostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'

class PostCreateSerializer(PostsSerializer):

    # populate the author field autmatically to current authenticated user
    # if the author filed will be prompt explicitly - it'll be ignored
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    published = serializers.BooleanField(default=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = 'id', 'username', 'email', 'last_request', 'last_login', 'date_joined', 'is_staff', 'is_active'

class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'



