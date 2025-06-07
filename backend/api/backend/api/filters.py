from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe


class RecipeQueryFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='favorite_filter',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='shopping_cart_filter',
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author')

    def favorite_filter(self, queryset, name, value):
        return self._filter_by_user_relation(queryset, 'favorited_by', value)

    def shopping_cart_filter(self, queryset, name, value):
        return self._filter_by_user_relation(queryset, 'shopping_carts', value)

    def _filter_by_user_relation(self, queryset, related_name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(**{f"{related_name}__user": self.request.user})
        return queryset
