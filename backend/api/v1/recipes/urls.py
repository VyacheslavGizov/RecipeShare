from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('tags', views.TagViewSet, basename='tags')
router.register('ingredients', views.IngredientViewSet,
                basename='ingredients')
router.register('recipes', views.RecipesViewSet, basename='recipes')
