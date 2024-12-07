from django.urls import include, path
from rest_framework import routers

from . import views


app_name = 'api'

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]