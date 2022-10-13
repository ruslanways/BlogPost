import copy
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from .models import Post, CustomUser, Like
from django.db.models import Count, Prefetch, F
from django.forms.models import model_to_dict
from .forms import (
    AddPostForm,
    CustomPasswordResetForm,
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CutomSetPasswordForm,
    UpdatePostForm,
)
from django.conf import settings
import redis
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import generics, status
from .serializers import (
    LikeSerializer,
    LikeDetailSerializer,
    MyTokenRefreshSerializer,
    PostDetailSerializer,
    PostSerializer,
    TokenRecoverySerializer,
    UserDetailSerializer,
    UserSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .permissions import (
    OwnerOrAdmin,
    OwnerOrAdminOrReadOnly,
    ReadForAdminCreateForAnonymous,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.reverse import reverse as reverse_rest
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

# just try simple redis connection with practice purposes
# look to AuthorListView with implementation
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class HomeView(ListView):
    paginate_by = 5

    template_name = "diary/index.html"
    queryset = (
        Post.objects.annotate(Count("like"))
        .select_related("author")
        .filter(published=True)
    )
    ordering = ["-updated", "-like__count"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ordering"] = "fresh"
        if self.request.user.is_authenticated:
            context["liked_by_user"] = self.queryset.filter(
                like__user=self.request.user
            )
        return context


class HomeViewLikeOrdered(HomeView):
    """Provide ordering by clicking on a link leads to the view."""

    ordering = ["-like__count", "-updated"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ordering"] = "liked"
        return context


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"

    # success_url = reverse_lazy('home')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        """make an authorization after signingup"""
        login(self.request, self.object)
        """and redirect to user profile with user.pk"""
        return redirect("author-detail", self.object.pk)


class Login(LoginView):
    template_name = "registration/login.html"
    form_class = CustomAuthenticationForm

    def get_default_redirect_url(self):
        return resolve_url("author-detail", self.request.user.pk)


class PasswordReset(PasswordResetView):
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CutomSetPasswordForm


class AuthorListView(UserPassesTestMixin, ListView):
    template_name = "diary/customuser_list.html"
    permission_denied_message = "Access for staff only!"

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        """
        Implemet a user-ordering using redis.
        That contains last ordering filed to make reverse ordering by field.
        p.s. it's better to implement it on a client side using js.
        """
        if self.kwargs.get("sortfield"):
            if (
                "-" + self.kwargs.get("sortfield")
                == redis_client.get("customordering").decode()
            ):
                redis_client.set(
                    name="customordering", value=self.kwargs.get("sortfield")
                )
            else:
                redis_client.set(
                    name="customordering", value="-" + self.kwargs.get("sortfield")
                )
        else:
            redis_client.mset({"customordering": "id"})
        return CustomUser.objects.annotate(
            Count("post", distinct=True),
            Count("like", distinct=True),
            Count("post__like", distinct=True),
        ).order_by(redis_client.get("customordering").decode())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = Post.objects.count()
        context["likes"] = Like.objects.count()
        return context


class AuthorDetailView(UserPassesTestMixin, DetailView, MultipleObjectMixin):
    template_name = "diary/customuser_detail.html"
    model = CustomUser
    paginate_by = 5
    permission_denied_message = "Access for staff or profile owner only!"

    def test_func(self):
        return self.request.user.is_staff or self.request.user.id == self.kwargs["pk"]

    def get_context_data(self, **kwargs):
        object_list = (
            self.get_object()
            .post_set.all()
            .annotate(Count("like"))
            .order_by("-updated", "-like__count")
        )
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context


class PostListView(UserPassesTestMixin, HomeView, ListView):
    template_name = "diary/post_list.html"
    queryset = Post.objects.annotate(Count("like")).select_related("author")
    # ordering = ['-updated', '-like__count'] inherit from parent class

    permission_denied_message = "Access for staff only!"

    def test_func(self):
        return self.request.user.is_staff


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = AddPostForm
    template_name = "diary/add-post.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    template_name = "diary/post_detail.html"
    queryset = Post.objects.annotate(Count("like")).select_related("author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["liked_by_user"] = self.queryset.filter(
                like__user=self.request.user
            )
        return context


class PostUpdateView(UserPassesTestMixin, UpdateView):
    permission_denied_message = "Access for staff or profile owner!"

    def test_func(self):
        return (
            self.request.user.is_staff
            or self.request.user.pk == self.get_object().author_id
        )

    model = Post
    form_class = UpdatePostForm
    template_name = "diary/post-update.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(PostUpdateView, DeleteView):
    template_name = "diary/post-delete.html"

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            "author-detail", kwargs={"pk": f"{self.get_object().author_id}"}
        )


class LikeCreateView(LoginRequiredMixin, View):
    redirect_field_name = "/"

    http_method_names = ["get"]

    def get(self, *args, **kwargs):
        try:
            like = Like.objects.create(
                user=self.request.user, post=Post.objects.get(pk=self.kwargs["pk"])
            )
            reply = "like created"
            status = 201
        except IntegrityError:
            like_to_delete = Like.objects.get(
                user=self.request.user, post=Post.objects.get(pk=self.kwargs["pk"])
            )
            like = copy.deepcopy(like_to_delete)
            like_to_delete.delete()
            reply = "like deleted"
            status = 204
        except Post.DoesNotExist:
            raise Http404
        return JsonResponse({reply: model_to_dict(like)}, status=status)


def getLikes(request, post_id):
    """
    View to help update likes for updateLike function in fetch.js
    """
    post = Post.objects.get(pk=post_id)
    count_likes = post.like_set.all()

    if request.user.is_authenticated and (request.user.like_set.all() & count_likes):
        heart = "&#10084;"
    else:
        heart = "&#9825;"
    return HttpResponse(heart + " " + str(count_likes.count()))


#######################################################################################################################
# Rest api with DRF


class UserListAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all().order_by("-last_request")
    serializer_class = UserSerializer
    permission_classes = (ReadForAdminCreateForAnonymous,)


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer

    def get_serializer_context(self):
        """
        Override parent's method.
        Add extra context 'obj' for using in serializer validator to get object.
        """
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "obj": self.get_object(),
        }

    permission_classes = (OwnerOrAdmin,)


class PostAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    filter_backends = DjangoFilterBackend, OrderingFilter
    ordering_fields = "id", "updated", "created"
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return (
            Post.objects.exclude(published=False)
            .annotate(likes=Count("like"))
            .order_by("-updated")
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    # permissions: Retrieve by All, Update by Author only, Delete by Author or Admin
    permission_classes = (OwnerOrAdminOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        """Make visible only published posts if user is not owner or admin."""
        instance = self.get_object()
        if (
            not instance.published
            and instance.author != request.user
            and not request.user.is_staff
        ):
            return Response(
                {"Forbidden": "Unpublished post can be retrieved by owner only!"},
                status=403,
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LikeAPIView(generics.ListAPIView):
    queryset = (
        Like.objects.values("created__date")
        .annotate(likes=Count("id"))
        .order_by("-created__date")
    )
    serializer_class = LikeSerializer
    filter_backends = DjangoFilterBackend, OrderingFilter
    filterset_fields = {
        "created": ["gte", "lte", "date__range"],
    }
    ordering_fields = "created", "likes"


class LikeDetailAPIView(generics.RetrieveAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeDetailSerializer


class LikeCreateDestroyAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LikeDetailSerializer

    # First version of view loginc.
    # def get(self, *args, **kwargs):
    #     try:
    #         like = Like.objects.create(user=self.request.user, post=Post.objects.get(pk=self.kwargs['post_id']))
    #         reply = 'like created'
    #         status = 201
    #     except IntegrityError:
    #         like_to_delete = Like.objects.get(user=self.request.user, post=Post.objects.get(pk=self.kwargs['post_id']))
    #         like = copy.deepcopy(like_to_delete)
    #         like_to_delete.delete()
    #         reply = 'like deleted'
    #         status = 204
    #     except Post.DoesNotExist:
    #         return Response({'status': "Post doesn't exist"}, status=404)
    #     return Response({reply: model_to_dict(like)}, status=status)


    # def post(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid()
    #     serializer.save(user=self.request.user)

    @extend_schema(
        description='Grant like on post.<br>If post already liked - remove like (ulike it).',
        responses={
            201: inline_serializer(
            name='Entities2', 
            fields={
                'like created': serializers.CharField(),
            }),
            204: inline_serializer(
            name='Entities3', 
            fields={
                'like deleted': serializers.CharField(),
            }),
        }
    )
    def get(self, *args, **kwargs):
        try:
            like_to_delete = Like.objects.get(
                user=self.request.user, post=Post.objects.get(pk=self.kwargs["post_id"])
            )
            #like = self.serializer_class(copy.deepcopy(like_to_delete), context={'request': self.request})
            like = copy.deepcopy(like_to_delete)
            like_to_delete.delete()
            reply = "like deleted"
            status = 204
        except Like.DoesNotExist:
            like = Like.objects.create(
                user=self.request.user, post=Post.objects.get(pk=self.kwargs["post_id"])
            )
            # like = self.serializer_class(
            #     data={
            #         'user': self.request.user,
            #         'post': Post.objects.get(pk=self.kwargs["post_id"]).get_absolute_url()
            #     },
            #     context={'request': self.request}
            # )
            # like.is_valid()
            # print(like.errors)
            # print(like.data)
            # like.save()
            reply = "like created"
            status = 201
        except Post.DoesNotExist:
            return Response({"status": "Post doesn't exist"}, status=404)
        return Response({reply: model_to_dict(like)}, status=status)
       #return Response({reply: like.data}, status=status)


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer


class TokenRecoveryAPIView(generics.GenericAPIView):
    """
    APIView to recover token in case of user forgot his password.
    All non-blacklisted REFRESH tokens (OutstandingToken) of the user gets blacklisted.
    And the new (pair) will generate and email to user.
    """

    serializer_class = TokenRecoverySerializer

    def post(self, request, *args, **kwargs):

        if len(request.data) != 1 or not request.data.get("email"):
            return Response(
                {"error": "please post email only"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"Oops!": "There is no user belogs mentioned emal"},
                status=status.HTTP_404_NOT_FOUND,
            )

        out_token = OutstandingToken.objects.filter(user=user)

        # if not out_token:
        #     return Response({"Oops!": "It seems you didn't have token-auth before"}, status=status.HTTP_404_NOT_FOUND)

        black_token = BlacklistedToken.objects.filter(token__user=user)

        for token_to_black in out_token:
            if not black_token.filter(token=token_to_black):
                BlacklistedToken.objects.create(token=token_to_black)

        refresh = RefreshToken.for_user(user)

        link_to_change_user = reverse_rest(
            "user-detail-update-destroy-api", request=request, args=[user.id]
        )

        send_mail(
            "BLOGPOST Token recovery",
            f"Here are your new access token expires in 5 min."
            f"\n\n'access': {str(refresh.access_token)}\n\n"
            "You can use it to change password by Post-request to: "
            f"{link_to_change_user}"
            "\n\nTherefore you could obtain new tokens pair by logging.",
            None,
            [user.email],
        )

        return Response({"Recovery email send": "Success"}, status=status.HTTP_200_OK)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Just an attempt to implement jwt-authorization for html site.
    The idea is to save refresh-token in cookies as most secure place
    and throw access-token to frontend (on frontend we can cath access-token
    in JS and store it within a variable (clousure scope) - I think it needs
    to make login-requests using AJAX(fetch)).
    """

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response = Response(
            {"access": serializer.validated_data["access"]}, status=status.HTTP_200_OK
        )
        response.set_cookie(
            key="refresh_token",
            value=serializer.validated_data["refresh"],
            httponly=True,
            samesite="Strict",
        )

        access = {"access": serializer.validated_data["access"]}
        return render(
            request, template_name="diary/aftertoken.html", context=access, status=200
        )


class RootAPIView(generics.GenericAPIView):
    @extend_schema(
        responses={200: inline_serializer(
            name='Entities', 
            fields={
                'posts': serializers.URLField(),
                'users': serializers.URLField(),
                'likes': serializers.URLField(),
            }
        )}
    )
    def get(self, request):
        return Response(
            {
                "posts": reverse_rest("post-list-create-api", request=request),
                "users": reverse_rest("user-list-create-api", request=request),
                "likes": reverse_rest("like-list-api", request=request),
            }
        )
