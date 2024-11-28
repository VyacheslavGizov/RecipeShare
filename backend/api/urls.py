from django.urls import include, path

from .v1.recipes.urls import router as recipe_router
from .v1.users.urls import router as user_router

app_name = 'api'


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(user_router.urls)),
    path('', include(recipe_router.urls)),
]
