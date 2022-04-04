import random
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def generate_confirmation_code():
    """простой генератор кодов"""
    confirmation_code = ''
    while confirmation_code == '':
        # исключены плохочитаемые буквы и цифры
        symbols = list('$#?=abcdefghijknpqrstuvwxyz'
                       'ABCDEFGHJKLMNOPQRSTUVWXYZ23456789')
        length_confirmation_code = settings.LENGTH_CONFORMATION_CODE
        # смешать
        random.shuffle(symbols)
        confirmation_code = ''.join(
            # случайно выбрать
            [random.choice(symbols)
             for index in range(length_confirmation_code)]
        )
    return confirmation_code


def get_tokens_for_user(user):
    """Запрос нового токена"""
    return RefreshToken.for_user(user).access_token
