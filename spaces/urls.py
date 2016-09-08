from django.conf.urls import url, include
from rest_framework import routers

from .viewsets import PlaceViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'', PlaceViewSet)


urlpatterns = [

    url(r'', include(router.urls)),
]
