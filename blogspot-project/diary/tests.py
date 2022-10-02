from pprint import pprint
from .serializers import PostSerializer
from .models import CustomUser, Post
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.settings import api_settings
from django.db.models import Count


class PostTestCase(APITestCase):
    def test_get(self):

        test_user_1 = CustomUser.objects.create(
            email="test1@ukr.net", username="TestUser1"
        )
        test_user_2 = CustomUser.objects.create(
            email="test2@ukr.net", username="TestUser2"
        )
        test_user_3 = CustomUser.objects.create(
            email="test3@ukr.net", username="TestUser3"
        )
        test_post_1 = Post.objects.create(
            title="TestPost1", author=test_user_1, content="Some test 1 content"
        )
        test_post_2 = Post.objects.create(
            title="TestPost2", author=test_user_3, content="Some test 2 content"
        )
        test_post_3 = Post.objects.create(
            title="TestPost3", author=test_user_1, 
            content="Some test 3 content",
            published=False
        )
        test_post_4 = Post.objects.create(
            title="TestPost4", author=test_user_2, content="Some test 4 content"
        )
        test_post_5 = Post.objects.create(
            title="TestPost5", author=test_user_3, content="Some test 5 content"
        )
        test_post_6 = Post.objects.create(
            title="TestPost6", author=test_user_3, content="Some test 6 content"
        )
        test_post_7 = Post.objects.create(
            title="TestPost7", author=test_user_1, content="Some test 7 content"
        )
        test_post_8 = Post.objects.create(
            title="TestPost8", author=test_user_2, content="Some test 8 content"
        )
        test_post_9 = Post.objects.create(
            title="TestPost9", author=test_user_3, content="Some test 9 content"
        )
        test_post_10 = Post.objects.create(
            title="TestPost10", author=test_user_2, content="Some test 10 content"
        )
        test_post_11 = Post.objects.create(
            title="TestPost11", author=test_user_3, content="Some test 11 content"
        )

        test_post_12 = Post.objects.create(
            title="TestPost12",
            author=test_user_3,
            content="Some test 11 content",
            published=False
        )

        queryset = (
            Post.objects.exclude(published=False)
            .annotate(likes=Count("like"))
            .order_by("-updated")
        )

        response = self.client.get(reverse("post-list-api"))

        serializer = PostSerializer(
            queryset, many=True, context={"request": response.wsgi_request}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            serializer.data[: api_settings.PAGE_SIZE], response.data["results"]
        )
