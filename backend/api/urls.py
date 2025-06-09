from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import СustomizeUserViewSet, RecipeViewSet, IngredientViewSet


router = DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', СustomizeUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
