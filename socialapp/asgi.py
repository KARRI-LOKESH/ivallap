# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from posts.consumers import ChatConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialapp.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<int:room_name>/", ChatConsumer.as_asgi()),  # WebSocket routing
        ])
    ),
})
