from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import СustomizeUserViewSet, RecipeViewSet, IngredientViewSet


router = DefaultRouter()

router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', СustomizeUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
