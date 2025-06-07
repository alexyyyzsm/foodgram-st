from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import (
    REGEX_USERNAME, REGEX_FIRST_NAME, REGEX_LAST_NAME, EMAIL_Validator
)
from constants import LEN_USERNAME, LEN_EMAIL, LEN_LAST_FIRST_NAME


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=LEN_USERNAME,
        unique=True,
        validators=[REGEX_USERNAME],
        help_text='Введите имя пользователя/логин'
    )

    email = models.EmailField(
        max_length=LEN_EMAIL,
        unique=True,
        validators=[
            EMAIL_Validator
        ],
        error_messages={
            'unique': 'Вводимая электронная почта уже зарегистрирована.',
        },
        verbose_name='Адрес электронной почты',
        help_text='Введите электронную почту'
    )

    first_name = models.CharField(
        max_length=LEN_LAST_FIRST_NAME,
        validators=[
            REGEX_FIRST_NAME
        ],
        verbose_name='Имя',
        help_text='Введите имя'
    )

    last_name = models.CharField(
        max_length=LEN_LAST_FIRST_NAME,
        validators=[
            REGEX_LAST_NAME
        ],
        verbose_name='Фамилия',
        help_text='Введите фамилию'
    )

    avatar = models.ImageField(
        upload_to='images/avatar/',
        blank=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return f"{self.username}, {self.email}, {self.first_name}, {self.last_name}"


class Subscription(models.Model):
    """Модель подписчиков."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Подписчик'
    )

    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписан на'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ['subscribed_to__username']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribed_to'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user}, {self.subscribed_to}'
