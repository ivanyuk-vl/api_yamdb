import os
from django.conf import settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    # 'djoser',
    'api.apps.ApiConfig',
    'reviews.apps.ReviewsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api_yamdb.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api_yamdb.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'),)

REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],

    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework_simplejwt.authentication.JWTAuthentication',
    # ],

    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 2,

    #  Ограничения на уровне проекта
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        # 'rest_framework.throttling.AnonRateThrottle',
        # Не будем подключать класс AnonRateThrottle глобально.
        # Подключим его только в тех view-классах или вьюсетах,
        # где надо установить лимиты для анонимов

        # Собственный лимит запросов
        'rest_framework.throttling.ScopedRateThrottle',

    ],
    # 'DEFAULT_THROTTLE_RATES': {
    #     'user': '10000/day',  # Лимит для UserRateThrottle,
    #     количество_запросов/период_времени
    #     'anon': '1000/day',  # Лимит для AnonRateThrottle
    #
    #     # Имена(ключи) для scope придумывает разработчик,
    #     # в меру собственной фантазии
    #     #  его можно подключить к отдельным view-классам или вьюсетам;
    #     #  скоуп указывается в атрибуте throttle_scope
    #     # 'low_request': '1/minute',
    #     }
}

# Преимущества JWT-токена в том, что прямо в нём записана информация
# о пользователе и сроке годности токена; системе не нужно каждый раз
# обращаться к базе данных, чтобы их сопоставить.
# Токен, созданный по стандарту JWT (JSON Web Token), состоит из трёх частей.
# Каждая из них записывается в формате JSON:
# header (англ. «заголовок») содержит служебную информацию;
# содержит два поля:
# алгоритм создания подписи — обычно применяется алгоритм HMAC-SHA256 или RSA;
# тип токена — это строка "JWT".

# payload (англ. «полезная нагрузка») хранит основные данные токена;
# хранит тип токена, timestamp со сроком его действия и информацию для
# аутентификации:

# signature (англ. «подпись») — подпись, ключ безопасности для защиты
# информации.
# Подпись гарантирует, что содержимое header и payload в токене не было
# изменено после создания. Специальный алгоритм генерирует подпись на основе
# содержимого header и payload. При кодировании этот алгоритм использует
# секретный ключ, который известен только серверу.

# После подготовки каждая из частей кодируется алгоритмом Base64URL.
# SIMPLE_JWT = {
#    'ACCESS_TOKEN_LIFETIME': timedelta(days=360),
#    'AUTH_HEADER_TYPES': ('Bearer',),
# }
