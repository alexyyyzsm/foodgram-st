from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator


REGEX_USERNAME = RegexValidator(
    r'^[a-zA-Z\d._@\+\-]+$',
    'Имя пользователя на латинице'
)

REGEX_FIRST_NAME = RegexValidator(
    regex=r'^[А-Я][-а-яёЁ]+$',
    message='Имя с большой буквы на кириллицы.'
)

REGEX_LAST_NAME = RegexValidator(
    regex=r'^[А-Я][-а-яёЁ]+$',
    message='Фамилия с большой буквы на кириллицы.'
)

EMAIL_Validator = EmailValidator(
    message=('Введите валидную электронну почту, '
             'например "name@domain.com".')
)
