from django.core.validators import (
    MinValueValidator, MaxValueValidator, RegexValidator
)
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=16,
        blank=False,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Название',
    )

    image = models.ImageField(
        upload_to='images/recipes/',
        blank=False,
        verbose_name='Картинка блюда',
        help_text='Загрузите картинку'
    )

    text = models.TextField(
        blank=False,
        verbose_name='Описание рецепта',
        help_text='Опишите рецепт приготовления'
    )

    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='IngredientRecipe', # Указываем свою промежуточную модель (таблицу т.к связь many-to-many)
        blank=False,
        verbose_name='Список ингредиентов'
    )

    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        validators=(
            MinValueValidator(limit_value=1,
                              message='Блюдо готово!'),
            MaxValueValidator(limit_value=1440,
                              message='Время приготовления ограничено сутками')
        ),
        verbose_name = 'Время приготовления в минутах',
        help_text='Укажите временя приготовления в минутах'
    )

    short_link = models.CharField(
        'Сокращенная ссылка',
        max_length=10,
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
    """Промежуточная модель для Ingredient и Recipe при many-to-many"""
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
        blank=False,
        validators=[
            MinValueValidator(limit_value=1,
                              message='Значение должно быть больше 0'),
            MaxValueValidator(limit_value=5000,
                              message='Увеличьте ед. изм., например 1000г=1кг')
        ],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredientrecipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient}, {self.recipe}, {self.amount}'


class Favorite(models.Model):
    """Модель избранного"""
    user = models.ForeignKey(
        to=User,
        verbose_name='Избранное пользователя',
        on_delete=models.CASCADE,
    )

    recipe = models.ForeignKey(
        to=Recipe,
        related_name='favorite',
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe}, {self.user}'


class ShoppingCart(models.Model):
    """Модель списка покупок пользователя"""
    user = models.ForeignKey(
        to=User,
        verbose_name='Список покупок пользователя',
        on_delete=models.CASCADE
    )

    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        return f'{self.recipe}, {self.user}'
