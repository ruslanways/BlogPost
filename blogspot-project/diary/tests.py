from pprint import pprint
import random
from .serializers import PostSerializer, PostDetailSerializer
from .models import CustomUser, Post
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.settings import api_settings
from django.db.models import Count
from rest_framework_simplejwt.tokens import RefreshToken


class PostAPITestCase(APITestCase):
   
    @classmethod
    def setUpTestData(cls):

        CustomUser.objects.create_user(
            email="admin@ukr.net", username="admin", password="fokker123", is_staff=True
        )
        CustomUser.objects.create_user(
            email="test1@ukr.net", username="TestUser1", password="fokker123"
        )
        CustomUser.objects.create_user(
            email="test2@ukr.net", username="TestUser2", password="fokker123"
        )
        CustomUser.objects.create_user(
            email="test3@ukr.net", username="TestUser3", password="fokker123"
        )

        cls.admin = CustomUser.objects.get(username="admin")
        cls.test_user_1 = CustomUser.objects.get(username="TestUser1")
        cls.test_user_2 = CustomUser.objects.get(username="TestUser2")
        cls.test_user_3 = CustomUser.objects.get(username="TestUser3")

        Post.objects.create(
            title="TestPost1", author=cls.test_user_1, content="Some test 1 content"
        )
        Post.objects.create(
            title="TestPost2", author=cls.test_user_3, content="Some test 2 content"
        )
        Post.objects.create(
            title="TestPost3",
            author=cls.test_user_1,
            content="Some test 3 content",
            published=False,
        )
        Post.objects.create(
            title="TestPost4", author=cls.test_user_2, content="Some test 4 content"
        )
        Post.objects.create(
            title="TestPost5", author=cls.test_user_3, content="Some test 5 content"
        )
        Post.objects.create(
            title="TestPost6", author=cls.test_user_3, content="Some test 6 content"
        )
        Post.objects.create(
            title="TestPost7", author=cls.test_user_1, content="Some test 7 content"
        )
        Post.objects.create(
            title="TestPost8", author=cls.test_user_2, content="Some test 8 content"
        )
        Post.objects.create(
            title="TestPost9", author=cls.test_user_3, content="Some test 9 content"
        )
        Post.objects.create(
            title="TestPost10", author=cls.test_user_2, content="Some test 10 content"
        )
        Post.objects.create(
            title="TestPost11", author=cls.test_user_3, content="Some test 11 content"
        )
        Post.objects.create(
            title="TestPost12",
            author=cls.test_user_3,
            content="Some test 11 content",
            published=False,
        )

        cls.test_post_1 = Post.objects.get(title="TestPost1")
        cls.test_post_2 = Post.objects.get(title="TestPost2")
        cls.test_post_3 = Post.objects.get(title="TestPost3")
        cls.test_post_4 = Post.objects.get(title="TestPost4")
        cls.test_post_5 = Post.objects.get(title="TestPost5")
        cls.test_post_6 = Post.objects.get(title="TestPost6")
        cls.test_post_7 = Post.objects.get(title="TestPost7")
        cls.test_post_8 = Post.objects.get(title="TestPost8")
        cls.test_post_9 = Post.objects.get(title="TestPost9")
        cls.test_post_10 = Post.objects.get(title="TestPost10")
        cls.test_post_11 = Post.objects.get(title="TestPost11")
        cls.test_post_12 = Post.objects.get(title="TestPost12")

        # Obtaining an access token for further authorization by JWT-tokens.
        cls.access_token_admin = RefreshToken.for_user(cls.admin).access_token
        cls.access_token_user1 = RefreshToken.for_user(cls.test_user_1).access_token
        cls.access_token_user2 = RefreshToken.for_user(cls.test_user_2).access_token
        cls.access_token_user3 = RefreshToken.for_user(cls.test_user_3).access_token

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

        # We just need to include Authorization header with our post-request below.
        # We also can use .credentials to set Authorization header with all requests:
        # self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
        # but we need 1 request to be Unauthorized, so we won't do it for now.
        # Or we can use standard Django session authorization backend:
        # self.client.login(username="TestUser1", password="fokker123")

        # Unauthorized
        response1 = self.client.post(
            reverse("post-list-api"),
            {"title": "New Test Post 1", "content": "Some conntent of New Test Post 1"},
        )

        # Use credentials to set Authorization header with all further requests:
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.access_token_user1}")

        # Bad request. Lack of "title".
        response2 = self.client.post(
            reverse("post-list-api"), {"content": "Some conntent of New Test Post 2"}
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
        )

        response5 = self.client.post(
            reverse("post-list-api"),
            {
                "title": "New Test Post 5",
                "content": "Some conntent of New Test Post 5",
                "created": "2022-03-01",
            },
        )

        response6 = self.client.post(
            reverse("post-list-api"),
            {
                "title": "New Test Post 6",
                "content": "Some conntent of New Test Post 6",
                "published": False,
            },
        )

        serializer = PostSerializer(
            Post.objects.get(title="New Test Post 3"),
            context={"request": response1.wsgi_request},
        )

        self.assertEqual(response1.status_code, 401)
        self.assertRaises(Post.DoesNotExist, Post.objects.get, title="New Test Post 1")

        self.assertEqual(response2.status_code, 400)
        self.assertRaises(Post.DoesNotExist, Post.objects.get, title="New Test Post 2")

        self.assertEqual(response3.status_code, 201)
        self.assertTrue(Post.objects.get(title="New Test Post 3"))
        self.assertEqual(serializer.data, response3.data)

        self.assertEqual(response4.status_code, 201)
        self.assertNotEqual(Post.objects.get(title="New Test Post 4").author_id, 3)
        self.assertEqual(
            Post.objects.get(title="New Test Post 4").author_id,
            response4.wsgi_request.user.id,
        )

        self.assertEqual(response5.status_code, 201)
        self.assertNotEqual(
            Post.objects.get(title="New Test Post 5").created, "2022-03-01"
        )

        self.assertEqual(response6.status_code, 201)
        self.assertEqual(Post.objects.get(title="New Test Post 6").published, False)

    def test_detail(self):

        # It's good idea to make a random choosing of Post object,
        # but we need to test both Post object with published Ture and False.
        # post_id = random.choice(Post.objects.all().values('id'))['id']
        # url = (reverse("post-detail-api", args=[post_id]))

        # published=True
        response1 = self.client.get(
            reverse("post-detail-api", args=[self.test_post_1.id])
        )
        # published=False
        response2 = self.client.get(
            reverse("post-detail-api", args=[self.test_post_12.id])
        )

        # published=False, but read by Owner
        response3 = self.client.get(
            reverse("post-detail-api", args=[self.test_post_12.id]),
            HTTP_AUTHORIZATION=f"JWT {self.access_token_user3}",
        )

        serializer1 = PostDetailSerializer(
            self.test_post_1,
            context={"request": response1.wsgi_request},
        )

        serializer3 = PostDetailSerializer(
            self.test_post_12,
            context={"request": response1.wsgi_request},
        )

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(serializer1.data, response1.data)

        self.assertEqual(response2.status_code, 403)

        self.assertEqual(response3.status_code, 200)
        self.assertEqual(serializer3.data, response3.data)

    def test_update(self):
        """
        IMHO.
        It's worth nothing that Post objects reachable with self.test_post_*
        only accessibe for retrieving so they don't change their state.
        In case we need to see wether the object is changed we should retrieve it from the object manager.
        """

        # Make a response just to obtain the wsgi_request for serializer to get serializer of clear Post object
        response = self.client.get("/")
        serializer_before_update = PostDetailSerializer(
            self.test_post_1, context={"request": response.wsgi_request}
        )

        # Unathorized
        response1 = self.client.put(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            {
                "title": "TestPost1 UPDATED by put ",
                "content": "Some UPDATED test 1 content",
            },
        )
        serializer_after_update1 = PostDetailSerializer(
            Post.objects.get(id=self.test_post_1.id),
            context={"request": response1.wsgi_request},
        )

        self.assertEqual(response1.status_code, 401)
        self.assertEqual(serializer_before_update.data, serializer_after_update1.data)

        # Authorized by owner
        response2 = self.client.put(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            {
                "title": "TestPost1 UPDATED by put",
                "content": "Some UPDATED test 1 content",
            },
            HTTP_AUTHORIZATION=f"JWT {self.access_token_user1}",
        )
        serializer_after_update2 = PostDetailSerializer(
            Post.objects.get(id=self.test_post_1.id),
            context={"request": response2.wsgi_request},
        )
        self.assertEqual(response2.status_code, 200)
        self.assertNotEqual(
            serializer_after_update1.data, serializer_after_update2.data
        )

        # Authorized by admin
        response3 = self.client.put(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            {
                "title": "TestPost1 UPDATED by put",
                "content": "Some UPDATED test 1 content",
            },
            HTTP_AUTHORIZATION=f"JWT {self.access_token_admin}",
        )
        serializer_after_update3 = PostDetailSerializer(
            Post.objects.get(id=self.test_post_1.id),
            context={"request": response3.wsgi_request},
        )
        self.assertEqual(response3.status_code, 200)
        self.assertNotEqual(
            serializer_after_update2.data, serializer_after_update3.data
        )

        # Update with unexisted fieldname
        response4 = self.client.put(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            {
                "title": "TestPost1 UPDATED by put",
                "contAnt": "Some UPDATED test 1 content",
            },
            HTTP_AUTHORIZATION=f"JWT {self.access_token_user1}",
        )
        serializer_after_update4 = PostDetailSerializer(
            Post.objects.get(id=self.test_post_1.id),
            context={"request": response4.wsgi_request},
        )
        self.assertEqual(response4.status_code, 200)
        self.assertEqual(
            serializer_after_update3.data["content"],
            serializer_after_update4.data["content"],
        )

        ##############################PATCH
        # Unathorized
        response1 = self.client.patch(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            {
                "title": "TestPost1 UPDATED by patch ",
                "content": "Some UPDATED with patch test 1 content",
            },
        )
        serializer_after_update5 = PostDetailSerializer(
            Post.objects.get(id=self.test_post_1.id),
            context={"request": response1.wsgi_request},
        )

        self.assertEqual(response1.status_code, 401)
        self.assertEqual(serializer_after_update4.data, serializer_after_update5.data)

        # Authorized by owner
        response2 = self.client.patch(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            {
                "title": "TestPost1 UPDATED by patch 2",
                "content": "Some UPDATED with patch 2 test 1 content",
            },
            HTTP_AUTHORIZATION=f"JWT {self.access_token_user1}",
        )
        serializer_after_update6 = PostDetailSerializer(
            Post.objects.get(id=self.test_post_1.id),
            context={"request": response2.wsgi_request},
        )
        self.assertEqual(response2.status_code, 200)
        self.assertNotEqual(
            serializer_after_update5.data, serializer_after_update6.data
        )

        # Authorized by admin
        response3 = self.client.patch(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            {
                "title": "TestPost1 UPDATED by patch 3",
                "content": "Some UPDATED with patch 3 test 1 content",
            },
            HTTP_AUTHORIZATION=f"JWT {self.access_token_admin}",
        )
        serializer_after_update7 = PostDetailSerializer(
            Post.objects.get(id=self.test_post_1.id),
            context={"request": response3.wsgi_request},
        )
        self.assertEqual(response3.status_code, 200)
        self.assertNotEqual(
            serializer_after_update6.data, serializer_after_update7.data
        )

        # Update with unexisted fieldname
        response4 = self.client.patch(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            {
                "title": "TestPost1 UPDATED by patch 4",
                "contAnt": "Some UPDATED with patch 4 test 1 content",
            },
            HTTP_AUTHORIZATION=f"JWT {self.access_token_user1}",
        )
        serializer_after_update8 = PostDetailSerializer(
            Post.objects.get(id=self.test_post_1.id),
            context={"request": response4.wsgi_request},
        )
        self.assertEqual(response4.status_code, 200)
        self.assertEqual(
            serializer_after_update7.data["content"],
            serializer_after_update8.data["content"],
        )

    def test_delete(self):

        # Unauthorized
        response1 = self.client.delete(
            reverse("post-detail-api", args=[self.test_post_1.id])
        )
        self.assertEqual(response1.status_code, 401)
        self.assertTrue(Post.objects.get(id=self.test_post_1.id))

        # Authorized by owner
        response2 = self.client.delete(
            reverse("post-detail-api", args=[self.test_post_1.id]),
            HTTP_AUTHORIZATION=f"JWT {self.access_token_user1}",
        )
        self.assertEqual(response2.status_code, 204)
        self.assertRaises(Post.DoesNotExist, Post.objects.get, title="TestPost1")

        # Authorized by admin
        response2 = self.client.delete(
            reverse("post-detail-api", args=[self.test_post_2.id]),
            HTTP_AUTHORIZATION=f"JWT {self.access_token_admin}",
        )
        self.assertEqual(response2.status_code, 204)
        self.assertRaises(Post.DoesNotExist, Post.objects.get, title="TestPost2")
