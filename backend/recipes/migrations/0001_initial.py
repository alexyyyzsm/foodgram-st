# Generated by Django 5.2.1 on 2025-06-05 20:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "add_time",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Время добавления в избранное"
                    ),
                ),
            ],
            options={
                "verbose_name": "Избранное пользователя",
                "verbose_name_plural": "Избранное пользователя",
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Название")),
                (
                    "measurement_unit",
                    models.CharField(max_length=16, verbose_name="Единица измерения"),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
            },
        ),
        migrations.CreateModel(
            name="IngredientRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=1, message="Значение должно быть больше 0"
                            ),
                            django.core.validators.MaxValueValidator(
                                limit_value=5000,
                                message="Увеличьте ед. изм., например 1000г=1кг",
                            ),
                        ],
                        verbose_name="Количество",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиенты в рецепте",
                "verbose_name_plural": "Ингредиенты в рецептах",
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256, verbose_name="Название")),
                (
                    "image",
                    models.ImageField(
                        help_text="Загрузите картинку",
                        upload_to="images/recipes/",
                        verbose_name="Картинка блюда",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="Опишите рецепт приготовления",
                        verbose_name="Описание рецепта",
                    ),
                ),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        help_text="Укажите временя приготовления в минутах",
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=1, message="Блюдо готово!"
                            ),
                            django.core.validators.MaxValueValidator(
                                limit_value=1440,
                                message="Время приготовления ограничено сутками",
                            ),
                        ],
                        verbose_name="Время приготовления в минутах",
                    ),
                ),
                (
                    "short_link",
                    models.CharField(
                        blank=True,
                        max_length=10,
                        unique=True,
                        verbose_name="Сокращенная ссылка",
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата публикации"
                    ),
                ),
            ],
            options={
                "verbose_name": "рецепт",
                "verbose_name_plural": "Рецепты",
                "ordering": ("-pub_date",),
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "список покупок",
                "verbose_name_plural": "Списки покупок",
            },
        ),
    ]
