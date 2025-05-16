import base64

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers, status

from users.models import User, Subscription

from recipes.models import IngredientRecipe, Recipe, Ingredient, Favorite, ShoppingCart


class Base64ImageField(serializers.ImageField):
    """Поле для кодирования изображения в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class СustomizeUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        ]

    def get_is_subscribed(self, data):
        request = self.context.get('request')

        if not request or request.user.is_anonymous:
            return False

        return Subscription.objects.filter(
            user=request.user, subscribed_to=data
        ).exists()


class CustomizeUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания User"""

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        ]

        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, data):
        fields = ['email', 'username', 'first_name', 'last_name', 'password']
        for field in fields:
            if field not in data:
                raise serializers.ValidationError(
                    {f'{field}': f'{field} обязательно к заполнению.'}
                )

        if data['email'] == data['username']:
            raise serializers.ValidationError(
                'Имя пользователя не должно совпадать '
                'с адресом электронной почты!'
            )

        if data['username'] == data['password']:
            raise serializers.ValidationError(
                'Имя пользователя и пароль не должны совпадать.'
            )

        if data['first_name'] == data['last_name']:
            raise serializers.ValidationError(
                'Имя и Фамилия не должны совпадать.'
            )

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

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
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
        if not self.initial_data.get('ingredients'):
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один ингредиент!'
            )
        return data

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Укажите хотя бы один игредиент.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        unique_ingredients = set()
        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    {'ingredients': 'Указан не существующий ингредиент.'},
                    code=status.HTTP_404_NOT_FOUND
                )
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    {'amount': 'Значение должно быть больше 0.'},
                    code=status.HTTP_400_BAD_REQUEST
                )
            unique_ingredients.add(ingredient['id'])

        if len(ingredients) != len(unique_ingredients):
            raise serializers.ValidationError(
                {'ingredients': 'Ингридиенты не должны дублироваться.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        return ingredients

    def _create_ingredients(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

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
            instance.save()
            return instance

    def to_representation(self, instance):
        """Сериализация ответа на POST-запрос."""
        serializer = RecipeDetailViewSerializer(instance) #, context=self.context)
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
    author = СustomizeUserSerializer()
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
        if not request or request.user.is_anonymous:
            return False

        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()


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
        return RecipeBriefSerializer(data.recipe).data

    class Meta:
        model = Favorite
        fields = [
            'user',
            'recipe'
        ]
        read_only_fields = ('user', 'recipe')


class ShoppingCartViewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart"""
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

    class Meta:
        model = ShoppingCart
        fields = [
            'user',
            'recipe'
        ]
        read_only_fields = ('user', 'recipe',)


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


class SubscriptionUserSerializer(СustomizeUserSerializer):
    """Сериализатор для модели User с его рецептами."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source="recipes.count")

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, instance):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')

        queryset = instance.recipes.all()
        if limit is not None and limit.isdigit():
            queryset = queryset[:int(limit)]

        return RecipeBriefSerializer(queryset, many=True).data
