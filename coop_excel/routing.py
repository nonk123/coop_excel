from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import path

from .consumers import ExcelConsumer

urlpatterns = [
    path("ws/", ExcelConsumer)
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(urlpatterns))
})
