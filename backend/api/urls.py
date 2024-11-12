from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from .v1.users.views import CustomUserViewSet


app_name = 'api'


router = routers.DefaultRouter()

router.register('users', CustomUserViewSet, 'users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
