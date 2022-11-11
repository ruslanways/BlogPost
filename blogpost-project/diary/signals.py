import datetime
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver



@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    pass
    print(f"user {user.username} logged in at {datetime.datetime.now()}")