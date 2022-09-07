import copy

from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from .models import Post, CustomUser, Like
from django.db.models import Count, Prefetch
from django.forms.models import model_to_dict
from .forms import AddPostForm, CustomPasswordResetForm, CustomUserCreationForm, CustomAuthenticationForm, CutomSetPasswordForm, UpdatePostForm
from django.conf import settings
import redis
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
import logging
from rest_framework import generics, viewsets
from .serializers import PostsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .permissions import OwnerOrAdmin


logger = logging.getLogger(__name__)

# just try simple redis connection with practice purposes
# look to AuthorListView with implementation
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class BaseView(View):
    def dispatch(self, request, *args, **kwargs):
        try: 
            response = super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f'Exception {type(e)}, User: {self.request.user}, Page requested: {self.request.get_full_path()}')
            return render(request, '400.html', status=400)
        return response


class HomeView(ListView, BaseView):

    paginate_by = 5

    template_name = 'diary/index.html'
    queryset = Post.objects.annotate(Count('like')).select_related('author').filter(published=True)
    ordering = ['-updated', '-like__count']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordering'] = 'fresh'
        if self.request.user.is_authenticated:
            context['liked_by_user'] = self.queryset.filter(like__user=self.request.user)
        return context


class HomeViewLikeOrdered(HomeView, BaseView):
    ordering = ['-like__count', '-updated']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordering'] = 'liked'
        return context


class PostListView(UserPassesTestMixin, HomeView, ListView, BaseView):

    template_name = 'diary/post_list.html'
    queryset = Post.objects.annotate(Count('like')).select_related('author')
    # ordering = ['-updated', '-like__count'] inherit from parent class

    permission_denied_message = 'Access for staff only!'

    def test_func(self):
        return self.request.user.is_staff


class PostDetailView(DetailView, BaseView):

    template_name = 'diary/post_detail.html'
    
    queryset = Post.objects.annotate(Count('like')).select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked_by_user'] = self.queryset.filter(like__user=self.request.user)
        return context


class AuthorListView(UserPassesTestMixin, ListView, BaseView):

    template_name = 'diary/customuser_list.html'

    permission_denied_message = 'Access for staff only!'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        """
        implemet a user-ordering using redis
        that contains last ordering filed to make reverse ordering by field
        p.s. it's better to implement it on client side using js
        """
        if self.kwargs.get('sortfield'):
            if '-' + self.kwargs.get('sortfield') == redis_client.get('customordering').decode():
                redis_client.set(name='customordering', value=self.kwargs.get('sortfield'))
            else:
                redis_client.set(name='customordering', value='-' + self.kwargs.get('sortfield'))
        else:
            redis_client.mset({'customordering': 'id'})
        return CustomUser.objects.annotate(
            Count('post', distinct=True), 
            Count('like', distinct=True), 
            Count('post__like', distinct=True)).order_by(redis_client.get('customordering').decode()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.count()
        context['likes'] = Like.objects.count()
        return context


class AuthorDetailView(UserPassesTestMixin, DetailView, MultipleObjectMixin, BaseView):

    template_name = 'diary/customuser_detail.html'

    model = CustomUser

    paginate_by = 5

    permission_denied_message = 'Access for staff or profile owner!'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.id == int(self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        object_list = self.get_object().post_set.all().annotate(Count('like')).order_by('-updated', '-like__count')
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context


class SignUp(CreateView, BaseView):

    form_class = CustomUserCreationForm
    template_name ='registration/signup.html'
    #success_url = reverse_lazy('home')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        """make an authorization after signingup"""
        login(self.request, self.object)
        """and redirect to user profile with user.pk"""
        return redirect('author-detail',  self.object.pk)


class Login(LoginView, BaseView):

    template_name = 'registration/login.html'

    form_class = CustomAuthenticationForm

    def get_default_redirect_url(self):
        return resolve_url('author-detail', self.request.user.pk)


class PasswordReset(PasswordResetView, BaseView):
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView, BaseView):
    form_class = CutomSetPasswordForm


class CreatePostView(LoginRequiredMixin, CreateView, BaseView):

    form_class = AddPostForm
    template_name ='diary/add-post.html'

    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CreateLikeView(LoginRequiredMixin, BaseView):

    redirect_field_name = '/'

    # def get_redirect_field_name(self):
    #     reverse_lazy('post-detail', kwargs={'pk': self.kwargs['pk']})
    
    http_method_names = ['get']

    def get(self, *args, **kwargs):
        try:
            like = Like.objects.create(user=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']))
            reply = 'like created'
            status = 201
        except IntegrityError:
            like_to_delete = Like.objects.get(user=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']))
            like = copy.deepcopy(like_to_delete)
            like_to_delete.delete()
            reply = 'like deleted'
            status = 204
        except Post.DoesNotExist:
            raise Http404
        # try:
        #     return redirect(f"{self.request.META['HTTP_REFERER']}#{self.kwargs['pk']}")
        # except KeyError:
        #     return redirect('post-detail', self.kwargs['pk'])
        return JsonResponse({reply: model_to_dict(like)}, status=status)


class PostUpdateView(UserPassesTestMixin, UpdateView, BaseView):

    permission_denied_message = 'Access for staff or profile owner!'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.pk == self.get_object().author_id

    model = Post
    form_class = UpdatePostForm
    template_name ='diary/post-update.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(PostUpdateView, DeleteView, BaseView):

    permission_denied_message = 'Access for staff or profile owner!'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.pk == self.get_object().author_id

    model = Post
    template_name ='diary/post-delete.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('author-detail', kwargs={'pk': f'{self.get_object().author_id}'})


def getLikes(request, pk):
    """
    View to help update likes for updateLike function in fetch.js
    """
    post = Post.objects.get(pk=pk)
    count_likes = post.like_set.all()

    if request.user.is_authenticated:
        heart = "&#10084;" if request.user.like_set.all() & count_likes else "&#9825;"
    else: 
        heart = "&#9825;"
    return HttpResponse(heart + " " + str(count_likes.count()))

###############################################################################
# Rest api with DRF

class PostsAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class PostAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostsSerializer
    # permissions: Retrieve All, Update by Author only, Delete by Author or Admin
    permission_classes = (OwnerOrAdmin, )


# class PostViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = PostsSerializer


class CreateLikeAPIView(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    def get(self, *args, **kwargs):
        try:
            like = Like.objects.create(user=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']))
            reply = 'like created'
            status = 201
        except IntegrityError:
            like_to_delete = Like.objects.get(user=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']))
            like = copy.deepcopy(like_to_delete)
            like_to_delete.delete()
            reply = 'like deleted'
            status = 204
        except Post.DoesNotExist:
            return Response({'status': "Post doesn't exist"}, status=404)

        return Response({reply: model_to_dict(like)}, status=status)


