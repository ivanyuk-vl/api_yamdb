from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """Запрос нового токена"""
    return RefreshToken.for_user(user).access_token
