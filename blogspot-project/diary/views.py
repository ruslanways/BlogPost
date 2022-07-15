from dis import dis
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .models import Post, CustomUser
from django.db.models import Count, Prefetch
from .forms import CustomUserCreationForm, CustomAuthenticationForm


class HomeView(ListView):
    template_name = 'diary/index.html'
    queryset = Post.objects.annotate(Count('like')).select_related('author').filter(published=True)
    ordering = ['-like__count', '-updated']


class PostListView(ListView):
    queryset = Post.objects.annotate(Count('like')).select_related('author')


class PostDetailView(DetailView):
    queryset = Post.objects.annotate(Count('like')).select_related('author')


class AuthorListView(ListView):
    def get_queryset(self):
        customordering = 'id'
        if self.kwargs.get('sortfield'):
            customordering = '-' + self.kwargs.get('sortfield')
        return CustomUser.objects.annotate(Count('post', distinct=True), Count('like', distinct=True), Count('post__like', distinct=True)).order_by(customordering)



class AuthorDetailView(DetailView):
    queryset = CustomUser.objects.all().prefetch_related(
        Prefetch('post_set', queryset=Post.objects.annotate(Count('like')).order_by('-like__count', '-updated'))
    )


class SignUp(CreateView):

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


class Login(LoginView):

    form_class = CustomAuthenticationForm

    def get_default_redirect_url(self):
        return resolve_url('author-detail', self.request.user.pk)

