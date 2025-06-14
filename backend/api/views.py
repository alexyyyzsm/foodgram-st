from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (
    Ingredient, IngredientRecipe, Recipe, Favorite, ShoppingCart
)
from users.models import Subscription, User
from .filters import RecipeQueryFilter
from .pagination import CustomPagePagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (UserDetailSerializer,
                          RecipeCreateViewSerializer,
                          IngredientSerializer,
                          FavoriteViewSerializer,
                          RecipeDetailViewSerializer,
                          ShoppingCartViewSerializer,
                          SubscriperViewSerializer,
                          SubscriptionUserSerializer,
                          AvatarUserSerializer
                          )
from .utils import get_short_link


class СustomizeUserViewSet(UserViewSet):
    """Вьюсет для модели User."""

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagePagination

    def get_queryset(self):
        if self.action == 'subscriptions':
            queryset = User.objects.filter(
                subscriptions__user=self.request.user
            )
            return queryset
        return super().get_queryset()

    def get_serializer_class(self):
        serializer_map = {
            'subscriptions': SubscriptionUserSerializer,
            'subscribe': SubscriperViewSerializer,
            'avatar': AvatarUserSerializer
        }
        return serializer_map.get(self.action,
                                  super().get_serializer_class())

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Получение информации о текущем пользователе."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request, **kwargs):
        """Добавление или удаление аватарки."""
        if request.method == 'PUT':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Список подписок пользователя."""
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        """Подписка на пользователя."""
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'subscribed_to': self.get_object()}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, subscribed_to=self.get_object())
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Отписка от пользователя."""
        subscribed_to = self.get_object()
        deleted_count = Subscription.objects.filter(user=request.user,
                                                    subscribed_to=subscribed_to).delete()[0]
        if deleted_count == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateViewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeQueryFilter
    pagination_class = CustomPagePagination

    # переопределяем метод ModelViewSet
    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            short_link=get_short_link(Recipe)
        )

    def get_serializer_class(self):
        action_serializers = {
            'favorite': FavoriteViewSerializer,
            'shopping_cart': ShoppingCartViewSerializer,
            'list': RecipeDetailViewSerializer,
            'retrieve': RecipeDetailViewSerializer,
        }
        return action_serializers.get(self.action, RecipeCreateViewSerializer)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, **kwargs):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        short_link = request.build_absolute_uri('/') + 'link/' + recipe.short_link

        return Response(
            {
                'short-link': short_link
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        """Добавление рецепта в избранное."""
        return self._handle_relation_action(request, model=Favorite, add=True)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        """Удаление рецепта из избранного."""
        return self._handle_relation_action(request, model=Favorite, add=False)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        return self._handle_relation_action(request=request,
                                            model=ShoppingCart,
                                            add=True)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        return self._handle_relation_action(request=request,
                                            model=ShoppingCart,
                                            add=False)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок пользователя в виде текстового файла."""
        ingredients_qs = (
            IngredientRecipe.objects
            .filter(recipe__recipe_shopping_carts__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        return self._download_shopping_cart(ingredients_qs)

    def _download_shopping_cart(self, ingredients):
        lines = [
            f"{ingredient['ingredient__name']} ({ingredient['ingredient__measurement_unit']}) - {ingredient['total_amount']}"
            for ingredient in ingredients
        ]

        shopping_list_text = '\n'.join(lines)

        return HttpResponse(shopping_list_text, content_type='text/plain')

    def _handle_relation_action(self, request, model, add):
        """Обработка добавления или удаления рецепта из связи (Избранное/Корзина)."""
        recipe = self.get_object()

        if add:
            serializer = self.get_serializer(
                data=request.data,
                context={
                    'request': request,
                    'recipe': recipe,
                    'model': model
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count = model.objects.filter(user=request.user, recipe=recipe).delete()[0]

        if deleted_count == 0:
            return Response({'errors': 'Рецепт не найден.'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ('^name',)
