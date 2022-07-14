from django.core.signals import request_finished
from django.dispatch import receiver


## just a simple try signals decorator styled

@receiver(request_finished)
def my_callback(sender, **kwargs):
    print("Request finished!")

