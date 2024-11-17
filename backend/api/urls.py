from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from .v1.users import views as user_views
from .v1.recipes import views as recipes_views


app_name = 'api'


router = routers.DefaultRouter()

router.register('users', user_views.CustomUserViewSet, basename='users')
router.register('tags', recipes_views.TagViewSet, basename='tags')
router.register('ingredients', recipes_views.IngredientViewSet,
                basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
