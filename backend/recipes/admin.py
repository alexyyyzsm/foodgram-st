from django.contrib import admin

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
    list_display = ['name', 'author', 'favorites']
    search_fields = ['name', 'author__username']
    list_filter = ['author']
    date_hierarchy = 'pub_date'

    @admin.display(description='Количество добавлений в избранное')
    def favorites(self, instance):
        return instance.favorite.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
