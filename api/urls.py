"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from rest_framework import routers
from rest_framework.urlpatterns import include

from .views import schema_view
from jwt_knox.viewsets import JWTKnoxAPIViewSet


router = routers.SimpleRouter(trailing_slash=False)
router.register(r'auth/jwt', JWTKnoxAPIViewSet, base_name='jwt_knox')

urlpatterns = [
    url(r'docs', schema_view, name='swagger-ui'),
    url(r'', include(router.urls)),
    url(r'accounts/', include('accounts.urls')),
]
