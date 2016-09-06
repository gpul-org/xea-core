from django.conf.urls import url, include
from rest_framework import routers
from .viewsets import UserViewSet
from .views import ActivateUserView

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    url(r'^activation/(?P<upk>[0-9]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ActivateUserView.as_view(), name='activation'),

    url(r'', include(router.urls)),
]