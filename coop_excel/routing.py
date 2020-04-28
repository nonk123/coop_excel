from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import re_path

from .consumers import ExcelConsumer

urlpatterns = [
    re_path("ws/$", ExcelConsumer)
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(urlpatterns))
})
