import datetime
from django.core.signals import request_finished
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from .models import Post
from django.dispatch import receiver


## just a try simple signals decorator styled

@receiver(post_save, sender=Post)
def save_post(sender, instance, **kwargs):
    print(f'New post! Title: "{instance.title}"')

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f'user {user.username} logged in at {datetime.datetime.now()}')

