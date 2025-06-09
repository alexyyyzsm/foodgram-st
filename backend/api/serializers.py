from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from constants import MIN_WEIGHT_INGREDIENT, MAX_WEIGHT_INGREDIENT
from recipes.models import (IngredientRecipe, Recipe, Ingredient,
                            Favorite, ShoppingCart)
from users.models import User, Subscription
from .fields import Base64ImageField


class UserDetailSerializer(UserSerializer):
    """Сериализатор для детального отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta(UserSerializer.Meta):
        """
        Наследуется от Meta родительского UserSerializer.
        Добавлены кастомные поля 'is_subscribed' и 'avatar'.
        """

        fields = list(UserSerializer.Meta.fields) + ['is_subscribed', 'avatar']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated and
                obj.subscribed_to.filter(user=request.user).exists())


class AvatarUserSerializer(UserDetailSerializer):
    """Сериализатор PUT-запроса на добавление или обновлении аватарки."""

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if not data.get('avatar'):
            raise serializers.ValidationError('Поле "avatar" обязательно для заполнения.')
        return data


class IngredientInRecipeCreateViewSerializer(serializers.ModelSerializer):
    """Сериализатор для поля ingredients в RecipeCreateSerializer"""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = [
            'id',
            'amount'
        ]

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise NotFound(detail=f"Ингредиент с ID {value} не найден.")
        return value

    def validate_amount(self, value):
        if value < MIN_WEIGHT_INGREDIENT or value > MAX_WEIGHT_INGREDIENT:
            raise serializers.ValidationError(
                f'Количество ингредиента должно быть больше {MIN_WEIGHT_INGREDIENT}'
                f'но меньше {MAX_WEIGHT_INGREDIENT}!'
            )
        return value


class RecipeCreateViewSerializer(serializers.ModelSerializer):
    """Сериализатор создания, изменения или удаления рецепта"""

    ingredients = IngredientInRecipeCreateViewSerializer(
        many=True,
        allow_empty=False
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'short_link'
        ]
        read_only_fields = ('author', 'short_link')

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Укажите хотя бы один ингредиент.'},
                code='invalid'
            )

        # Используем генератор для получения списка ID ингредиентов
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        # Сравниваем длину списка с длиной множества (set) для проверки дубликатов
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны дублироваться.'},
                code='invalid'
            )

        return data

    def _create_ingredients(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    def create(self, data):
        with transaction.atomic():
            ingredients = data.pop('ingredients')
            recipe = Recipe.objects.create(**data)
            self._create_ingredients(ingredients, recipe)
            return recipe

    def update(self, obj, data):
        with transaction.atomic():
            ingredients = data.pop('ingredients')
            IngredientRecipe.objects.filter(recipe=obj).delete()
            self._create_ingredients(ingredients, obj)
            instance = super().update(obj, data)
            return instance

    def to_representation(self, instance):
        """Сериализация ответа на POST-запрос."""

        serializer = RecipeDetailViewSerializer(instance,
                                                context=self.context)
        return serializer.data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]

class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для поля ingredients в RecipeReadSerializer."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]


class RecipeDetailViewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe при GET-запросах."""

    author = UserDetailSerializer()
    ingredients = IngredientInRecipeReadSerializer(
        many=True, source='ingredients_in_recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')

        return (request and request.user.is_authenticated and
                request.user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')

        return (request and request.user.is_authenticated and
                request.user.user_shopping_carts.filter(recipe=obj).exists())


class RecipeBriefSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта"""

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class FavoriteViewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite"""

    class Meta:
        model = Favorite
        fields = [
            'user',
            'recipe'
        ]
        read_only_fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context['request'].user
        recipe = self.context['recipe']
        model = self.context['model']

        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт "{recipe.name}" уже добавлен.'
            )
        return data

    def to_representation(self, data):
        return RecipeBriefSerializer(data.recipe, context=self.context).data


class ShoppingCartViewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart"""

    class Meta:
        model = ShoppingCart
        fields = [
            'user',
            'recipe'
        ]
        read_only_fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        model = self.context.get('model')
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт - {recipe.name} уже добавлен!'
            )
        return data

    def to_representation(self, obj):
        serializer = RecipeBriefSerializer(obj.recipe)
        return serializer.data


class SubscriperViewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    class Meta:
        model = Subscription
        fields = ('user', 'subscribed_to',)
        read_only_fields = ('user', 'subscribed_to',)

    def validate(self, data):
        user = self.context.get('request').user
        subscribed_to = self.context.get('subscribed_to')

        if user == subscribed_to:
            raise serializers.ValidationError('Нельзя подписаться на себя!')

        if Subscription.objects.filter(user=user, subscribed_to=subscribed_to).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на {subscribed_to.username}!'
            )

        return data

    def to_representation(self, instance):
        serializer = SubscriptionUserSerializer(
            instance.subscribed_to,
            context=self.context
        )
        return serializer.data


class SubscriptionUserSerializer(UserDetailSerializer):
    """Сериализатор для модели User с его рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source="recipes.count")

    class Meta(UserDetailSerializer.Meta):
        model = User
        fields = list(UserDetailSerializer.Meta.fields) + ['recipes', 'recipes_count']

    def get_recipes(self, instance):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')

        queryset = instance.recipes.all()
        if limit is not None and limit.isdigit():
            queryset = queryset[:int(limit)]

        return RecipeBriefSerializer(queryset, many=True, context=self.context).data
