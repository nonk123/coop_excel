from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

urlpatterns = []

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(urlpatterns))
})
