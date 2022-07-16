from django.core.signals import request_finished
from django.db.models.signals import post_save
from .models import Post
from django.dispatch import receiver


## just a try simple signals decorator styled

@receiver(post_save, sender=Post)
def save_post(sender, instance, **kwargs):
    print(f'New post! Title: "{instance.title}"')

