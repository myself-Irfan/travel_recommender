from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

from travel_recommender.utils import get_env_or_raise, str_to_bool

# ---------------------------------------------------------------------
# Paths & Environment
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if not ENV_PATH.exists():
    raise ImproperlyConfigured(
        ".env file not found. Did you forget to create one?"
    )

load_dotenv(dotenv_path=ENV_PATH)

# ---------------------------------------------------------------------
# Core Settings
# ---------------------------------------------------------------------

SECRET_KEY = get_env_or_raise('SECRET_KEY')
DEBUG = str_to_bool(get_env_or_raise("DEBUG"))

ALLOWED_HOSTS = [
    host.strip()
    for host in get_env_or_raise("ALLOWED_HOSTS").split(",")
    if host.strip()
]

# ---------------------------------------------------------------------
# Application Definition
# ---------------------------------------------------------------------


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # app files
    'drf_yasg',
    'rest_framework',
    'travel'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "travel_recommender.middleware.request_response_logger.RequestResponseLoggerMiddleware",
]

ROOT_URLCONF = 'travel_recommender.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'travel_recommender.wsgi.application'

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------

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

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static Files
# ---------------------------------------------------------------------

STATIC_URL = 'static/'

# ---------------------------------------------------------------------
# REST Framework Config
# ---------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(get_env_or_raise('PAGINATION_PAGE_SIZE')),
}

# ---------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': get_env_or_raise("REDIS_URL"),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        },
        'KEY_PREFIX': 'air_quality',
        'TIMEOUT': 3600
    }
}

CACHE_TTL = int(get_env_or_raise("CACHE_TTL_IN_SECONDS"))
DISTRICTS_CACHE_TTL=int(get_env_or_raise('DISTRICTS_CACHE_TTL_IN_SECONDS'))
WEATHER_CACHE_TTL=int(get_env_or_raise('WEATHER_CACHE_TTL_IN_SECONDS'))

# ---------------------------------------------------------------------
# External APIs
# ---------------------------------------------------------------------

OPEN_METEO_BASE_URL = get_env_or_raise('OPEN_METEO_BASE_URL')
DISTRICTS_JSON_URL = get_env_or_raise('DISTRICTS_JSON_URL')
REQUEST_TIMEOUT = int(get_env_or_raise('REQUEST_TIMEOUT_IN_SECONDS'))

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

from travel_recommender.structlog_config import configure_structlog
configure_structlog()