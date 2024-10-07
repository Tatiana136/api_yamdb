from django.core.exceptions import ValidationError


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError("Имя пользователя 'me' недоступно.")
    return value
