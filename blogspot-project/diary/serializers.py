from dataclasses import fields
from email.policy import default
from rest_framework import serializers
from .models import Like, Post


class PostsSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    published = serializers.BooleanField(default=True)

    class Meta:
        model = Post
        fields = '__all__'


