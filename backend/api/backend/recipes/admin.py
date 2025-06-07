from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name']
    ordering = ['name']


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'amount']
    search_fields = ['recipe__name', 'ingredient__name']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author']
    search_fields = ['name', 'author__username']
    list_filter = ['author']
    date_hierarchy = 'pub_date'

    @admin.display(description='Количество добавлений в избранное')
    def favorites(self, instance):
        return instance.favorite.count()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Проверка для создания нового объекта
            form.base_fields['ingredients'].required = True
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.ingredients.exists() and not change:  # Проверка после сохранения
            obj.delete()  # Удаляем рецепт, если ингредиентов нет
            raise ValidationError("Рецепт не может быть создан без ингредиентов.")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
