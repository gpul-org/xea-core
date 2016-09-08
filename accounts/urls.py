from django.conf.urls import url, include
from rest_framework import routers
from .viewsets import UserViewSet

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)

activation = UserViewSet.as_view({
    'get': 'activate'
})

urlpatterns = [
    url(r'^users/(?P<upk>[0-9]+)/activation/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activation, name='activation'),

    url(r'', include(router.urls)),
]