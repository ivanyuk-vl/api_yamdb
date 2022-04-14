from datetime import datetime
import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from api_yamdb.settings import REVIEWS

USERNAME_PATTERN_MATCH_ERROR = (
    'Введите действительное имя пользоваятеля. '
    'Оно может состоять только из букв, чисел, '
    'и @/./+/-/_ символов.'
)
USERNAME_ME_ERROR = 'Недопустимое имя пользователя \'me\'.'
YEAR_ERROR = 'Недопустимый год {}. Год должен быть меньше либо равен {}.'
MIN_SCORE_ERROR = 'Оценка не может быть меньше {}.'
MAX_SCORE_ERROR = 'Оценка не может быть больше {}.'


class UsernameValidator(RegexValidator):
    regex = r'^[\w.@+-]+\Z'
    message = USERNAME_PATTERN_MATCH_ERROR


class UsernameMeValidator(RegexValidator):
    regex = re.compile(r'\Ame\Z', re.IGNORECASE)
    inverse_match = True
    message = USERNAME_ME_ERROR


def year_validator(year):
    current_year = datetime.now().year
    if not (year <= current_year):
        raise ValidationError(YEAR_ERROR.format(
            year, current_year
        ))


def min_score_validator(score):
    if score < REVIEWS['MIN_SCORE']:
        raise ValidationError(MIN_SCORE_ERROR.format(REVIEWS['MIN_SCORE']))


def max_score_validator(score):
    if score > REVIEWS['MAX_SCORE']:
        raise ValidationError(MAX_SCORE_ERROR.format(REVIEWS['MAX_SCORE']))
