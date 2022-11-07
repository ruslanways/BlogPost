import datetime
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in
from .models import Post, Like
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


channel_layer = get_channel_layer()

@receiver(post_save, sender=Like)
def new_like(sender, instance, **kwargs):
    async_to_sync(channel_layer.group_send)(
        'likes',
        {
            "type": "chat_message", 
            "message": "1212341324, 213413252345"
        }
    )

# @receiver(post_delete, sender=Like)
# def new_like(sender, instance, **kwargs):
#     # channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         'likes',
#         {
#             "type": "chat_message", 
#             #"message": f"{instance.post.id}, {Post.objects.get(pk=instance.post.id).like_set.count()}"
#             "message": "12123asdfa41324, 21341adsfa3252345"
#         }
#     )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    pass
    print(f"user {user.username} logged in at {datetime.datetime.now()}")