import random
import secrets
import string

from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def get_short_link(model, length=6):
    chars = string.ascii_letters + string.digits
    while True:
        short_link = ''.join(secrets.choice(chars) for _ in range(length))
        if not model.objects.filter(short_link=short_link).exists():
            return short_link


def recipe_absolute_uri(request, short_link):
    recipe = get_object_or_404(Recipe, short_link=short_link)
    recipe_id = recipe.id
    return redirect(
        request.build_absolute_uri('/') + f'recipes/{recipe_id}/'
    )