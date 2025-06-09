from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from django.db import models

from constants import (MIN_WEIGHT_INGREDIENT, MAX_WEIGHT_INGREDIENT,
                       MIN_COOKING_TIME, MAX_COOKING_TIME, LEN_SHORT_LINK,
                       LEN_INGREDIENT_NAME, LEN_MEASUREMENT_UNIT,
                       LEN_RECIPE_NAME)
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=LEN_INGREDIENT_NAME,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=LEN_MEASUREMENT_UNIT,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_name_measurement'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=LEN_RECIPE_NAME,
        verbose_name='Название'
    )

    image = models.ImageField(
        upload_to='images/recipes/',
        verbose_name='Картинка блюда',
        help_text='Загрузите картинку'
    )

    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Опишите рецепт приготовления'
    )

    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='IngredientRecipe', # Указываем свою промежуточную модель (таблицу т.к связь many-to-many)
        verbose_name='Список ингредиентов'
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(limit_value=MIN_COOKING_TIME,
                              message=f'Минимальное время приготовления {MIN_COOKING_TIME} мин'),
            MaxValueValidator(limit_value=MAX_COOKING_TIME,
                              message=f'Время приготовления ограничено сутками {MAX_COOKING_TIME} мин')
        ),
        verbose_name = 'Время приготовления в минутах',
        help_text='Укажите временя приготовления в минутах'
    )

    short_link = models.CharField(
        'Сокращенная ссылка',
        max_length=LEN_SHORT_LINK,
        unique=True,
        blank=True
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Промежуточная модель для Ingredient и Recipe при many-to-many."""

    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe'
    )

    ingredient = models.ForeignKey(
        to=Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )

    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(limit_value=MIN_WEIGHT_INGREDIENT,
                              message=f'Значение должно быть больше {MIN_WEIGHT_INGREDIENT}'),
            MaxValueValidator(limit_value=MAX_WEIGHT_INGREDIENT,
                              message=f'Максимальное значение {MAX_WEIGHT_INGREDIENT}')
        ],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ['recipe__pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredientrecipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient}, {self.recipe}, {self.amount}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        to=User,
        related_name='favorites',
        verbose_name='Избранное пользователя',
        on_delete=models.CASCADE,
    )

    recipe = models.ForeignKey(
        to=Recipe,
        related_name='recipe_favorites',
        verbose_name='Рецепт в избранном пользователя',
        on_delete=models.CASCADE
    )

    add_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время добавления в избранное'
    )

    class Meta:
        verbose_name = 'Избранное пользователя'
        verbose_name_plural = 'Избранное пользователя'
        ordering = ['-add_time']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe}, {self.user}'


class ShoppingCart(models.Model):
    """Модель списка покупок пользователя."""

    user = models.ForeignKey(
        to=User,
        related_name='user_shopping_carts',
        verbose_name='Список покупок пользователя',
        on_delete=models.CASCADE
    )

    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ['-recipe__pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        return f'{self.recipe}, {self.user}'
