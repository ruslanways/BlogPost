"""
ASGI config for blogpost project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

django_app = get_asgi_application()
import diary.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.settings')



application = ProtocolTypeRouter(
    {
        'http': django_app,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(diary.routing.websocket_urlpatterns))
        ),
    }
)
