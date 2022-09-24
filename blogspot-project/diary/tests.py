from pprint import pprint
from .serializers import PostsSerializer
from .models import CustomUser, Post
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.request import Request
from rest_framework import serializers
from rest_framework.settings import api_settings
from unittest import mock


class PostsTestCase(APITestCase):

    def test_get(self):

        test_user_1 = CustomUser.objects.create(email='test1@ukr.net', username='TestUser1')
        test_user_2 = CustomUser.objects.create(email='test2@ukr.net', username='TestUser2')
        test_user_3 = CustomUser.objects.create(email='test3@ukr.net', username='TestUser3')
        test_post_1 = Post.objects.create(title='TestPost1', author= test_user_1, content='Some test 1 content')
        test_post_2 = Post.objects.create(title='TestPost2', author= test_user_3, content='Some test 2 content')
        test_post_3 = Post.objects.create(title='TestPost3', author= test_user_1, content='Some test 3 content')
        test_post_4 = Post.objects.create(title='TestPost4', author= test_user_2, content='Some test 4 content')
        test_post_5 = Post.objects.create(title='TestPost5', author= test_user_3, content='Some test 5 content')

        response = self.client.get(reverse('post-list-api'), data={'ordering': 'id'})

        print(response.wsgi_request)

        serializer = PostsSerializer([test_post_2, test_post_1, test_post_3, test_post_4, test_post_5], many=True)


        pprint(type(serializer.data))
        pprint(type(response.data))

        if api_settings.DEFAULT_PAGINATION_CLASS:
            self.assertEqual(serializer.data, response.data['results'])
        else:
            self.assertEqual(serializer.data, response.data)

