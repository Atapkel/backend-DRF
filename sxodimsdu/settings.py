from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@y%=w72m-_n50wxx=2ajb7$o#4stnrqwmxqo)(+zouui-m)_&^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'silk',
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'storages',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'sxodimsdu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sxodimsdu.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

if not DEBUG == False:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'railway',
            'USER': 'postgres',
            'PASSWORD': 'vQGFsGuWyEHifNBctBQJjGJoyDOxzFqm',
            'HOST': 'yamabiko.proxy.rlwy.net',
            'PORT': '59715',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'sxodimsdu_db',
            'USER': 'postgres',
            'PASSWORD': '0000',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

DOMAIN_NAME = 'http://localhost:8080'

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'core.Student'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',  # Limit for anonymous users (100 requests per day)
        'user': '1000/day',  # Limit for authenticated users (1000 requests per day)

    }
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'SDU SXODIM API Project',
    'DESCRIPTION': 'Documentation for your amazing API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # Django test client compatibility
    # Other optional settings...
}
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",  # Update with your Redis server details
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://default:TXnvTOTIziikvLXXnPsFkmCNjLGJdqNJ@centerbeam.proxy.rlwy.net:12295",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "TXnvTOTIziikvLXXnPsFkmCNjLGJdqNJ",  # Optional if included in URL
        }
    }
}


# Minio (S3-compatible) Configuration
AWS_ACCESS_KEY_ID = 'Pkzzomg7LQmRjtMwB2t9'  # Railway env var for access key
AWS_SECRET_ACCESS_KEY = 'oznita1BV1wdSjp6FTb5xuiMtfH6BZHVWYPkUX1k'  # Railway env var for secret key
AWS_STORAGE_BUCKET_NAME = 'sxodimsdu-bucket'  # Name of your Minio bucket (e.g., "rub-volume")
AWS_S3_ENDPOINT_URL = 'https://bucket-production-34fe.up.railway.app:443'  # Railway endpoint (e.g., "https://bucket-production-34fe.up.r...")
AWS_S3_ADDRESSING_STYLE = 'path'  # Required for Minio
AWS_S3_USE_SSL = True  # Set to True if Railway uses HTTPS
AWS_DEFAULT_ACL = 'public-read'  # Adjust if files need to be private

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # Cache images for 24 hours
}

# Media Files Configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'



CELERY_BROKER_URL =  "redis://default:TXnvTOTIziikvLXXnPsFkmCNjLGJdqNJ@centerbeam.proxy.rlwy.net:12295/0"
CELERY_RESULT_BACKEND =  "redis://default:TXnvTOTIziikvLXXnPsFkmCNjLGJdqNJ@centerbeam.proxy.rlwy.net:12295/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'# settings.py

# Email Configuration (Gmail SMTP)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
# EMAIL_USE_TLS = True  # Use TLS for port 587
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'mikooosia005@gmail.com'
EMAIL_HOST_PASSWORD = 'ootgdxkfvsdctklf'
# DEFAULT_FROM_EMAIL = 'mikooosia005@gmail.com'