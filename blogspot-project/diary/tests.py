from pprint import pprint
from .serializers import PostSerializer
from .models import CustomUser, Post
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.settings import api_settings
from django.db.models import Count
from rest_framework_simplejwt.tokens import RefreshToken


class PostAPITestCase(APITestCase):
    def setUp(self):

        self.test_user_1 = CustomUser.objects.create_user(
            email="test1@ukr.net", username="TestUser1", password="fokker123"
        )
        self.test_user_2 = CustomUser.objects.create_user(
            email="test2@ukr.net", username="TestUser2", password="fokker123"
        )
        self.test_user_3 = CustomUser.objects.create_user(
            email="test3@ukr.net", username="TestUser3", password="fokker123"
        )
        self.test_post_1 = Post.objects.create(
            title="TestPost1", author=self.test_user_1, content="Some test 1 content"
        )
        self.test_post_2 = Post.objects.create(
            title="TestPost2", author=self.test_user_3, content="Some test 2 content"
        )
        self.test_post_3 = Post.objects.create(
            title="TestPost3",
            author=self.test_user_1,
            content="Some test 3 content",
            published=False,
        )
        self.test_post_4 = Post.objects.create(
            title="TestPost4", author=self.test_user_2, content="Some test 4 content"
        )
        self.test_post_5 = Post.objects.create(
            title="TestPost5", author=self.test_user_3, content="Some test 5 content"
        )
        self.test_post_6 = Post.objects.create(
            title="TestPost6", author=self.test_user_3, content="Some test 6 content"
        )
        self.test_post_7 = Post.objects.create(
            title="TestPost7", author=self.test_user_1, content="Some test 7 content"
        )
        self.test_post_8 = Post.objects.create(
            title="TestPost8", author=self.test_user_2, content="Some test 8 content"
        )
        self.test_post_9 = Post.objects.create(
            title="TestPost9", author=self.test_user_3, content="Some test 9 content"
        )
        self.test_post_10 = Post.objects.create(
            title="TestPost10", author=self.test_user_2, content="Some test 10 content"
        )
        self.test_post_11 = Post.objects.create(
            title="TestPost11", author=self.test_user_3, content="Some test 11 content"
        )

        self.test_post_12 = Post.objects.create(
            title="TestPost12",
            author=self.test_user_3,
            content="Some test 11 content",
            published=False,
        )

    def test_list(self):

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

    def test_create(self):

        # Obtaining an access token for further authorization by JWT-tokens.
        # We just need to include Authorization header with our post-request below.
        access_token = RefreshToken.for_user(self.test_user_1).access_token
        # We also can use .credentials to add Authorization header with all requests:
        # self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
        # but we need 1 request to be Unauthorized, so we won't do it for now.

        # Or we can use standard Django session authorization backend:
        # self.client.login(username="TestUser1", password="fokker123")

        response1 = self.client.post(
            reverse("post-list-api"),
            {"title": "New Test Post 1", "content": "Some conntent of New Test Post 1"},
            HTTP_AUTHORIZATION=f"JWT {access_token}",
        )

        response2 = self.client.post(
            reverse("post-list-api"),
            {"content": "Some conntent of New Test Post 2"},
            HTTP_AUTHORIZATION=f"JWT {access_token}",
        )

        response3 = self.client.post(
            reverse("post-list-api"),
            {"title": "New Test Post 3", "content": "Some conntent of New Test Post 3"},
        )

        response4 = self.client.post(
            reverse("post-list-api"),
            {
                "title": "New Test Post 4",
                "content": "Some conntent of New Test Post 4",
                "author": 3,
            },
            HTTP_AUTHORIZATION=f"JWT {access_token}",
        )

        response5 = self.client.post(
            reverse("post-list-api"),
            {
                "title": "New Test Post 5",
                "content": "Some conntent of New Test Post 5",
                "created": "2022-03-01",
            },
            HTTP_AUTHORIZATION=f"JWT {access_token}",
        )

        response6 = self.client.post(
            reverse("post-list-api"),
            {
                "title": "New Test Post 6",
                "content": "Some conntent of New Test Post 6",
                "published": False,
            },
            HTTP_AUTHORIZATION=f"JWT {access_token}",
        )

        serializer = PostSerializer(
            Post.objects.get(title="New Test Post 1"),
            context={"request": response1.wsgi_request},
        )

        self.assertEqual(response1.status_code, 201)
        self.assertTrue(Post.objects.get(title="New Test Post 1"))
        self.assertEqual(serializer.data, response1.data)

        self.assertEqual(response2.status_code, 400)
        self.assertRaises(Post.DoesNotExist, Post.objects.get, title="New Test Post 2")

        self.assertEqual(response3.status_code, 401)
        self.assertRaises(Post.DoesNotExist, Post.objects.get, title="New Test Post 3")

        self.assertEqual(response4.status_code, 201)
        self.assertNotEqual(Post.objects.get(title="New Test Post 4").author_id, 3)
        self.assertEqual(Post.objects.get(title="New Test Post 4").author_id, 1)

        self.assertEqual(response5.status_code, 201)
        self.assertNotEqual(Post.objects.get(title="New Test Post 5").created, "2022-03-01")

        self.assertEqual(response6.status_code, 201)
        self.assertEqual(Post.objects.get(title="New Test Post 6").published, False)

    def test_detail(self):
        pass

    def test_update(self):
        pass

    def test_delete(self):
        pass
