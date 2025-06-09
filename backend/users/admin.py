from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['first_name', 'last_name', 'username', 'email']
    search_fields = ['first_name', 'last_name', 'username', 'email']

    @admin.display(description='Рецепты')
    def recipe_count(self, obj):
        """Возвращает количество рецептов, созданных пользователем."""
        return obj.recipes.count()

    @admin.display(description='Подписчики')
    def subscriber_count(self, obj):
        """Возвращает количество подписчиков пользователя."""
        return obj.subscribed_to.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscribed_to']
    search_fields = ['user__username', 'subscribed_to__username']


admin.site.unregister(Group)
