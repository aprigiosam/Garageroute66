"""
SETTINGS MINIMALISTA - DEPLOY GRATUITO
=======================================
Use este arquivo para deploy rápido sem features pesadas.
Para usar: renomeie para settings.py ou configure DJANGO_SETTINGS_MODULE=oficina.settings_minimal

IMPORTANTE: Este settings usa SQLite em produção (limitado mas funciona para começar)
Depois migre para PostgreSQL quando crescer.
"""

import os
from pathlib import Path
import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-change-me-in-production'),
    ALLOWED_HOSTS=(list, []),
)

# Reading .env file (if exists)
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# ALLOWED_HOSTS - aceita string separada por vírgula ou lista
allowed_hosts_list = env.list('ALLOWED_HOSTS', default=[])
if allowed_hosts_list:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_list if h.strip()]
else:
    # Fallback para garantir que sempre haja um valor, caso a variável de ambiente não seja definida
    # ou esteja vazia. Isso deve ser sobrescrito pela variável de ambiente no Render.
    ALLOWED_HOSTS = ['garageroute66.onrender.com', '*.onrender.com', 'localhost', '127.0.0.1']

# Application definition - MINIMALISTA
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Servir arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oficina.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'oficina.wsgi.application'

# Database - PostgreSQL (persistente) ou SQLite (local)
# Para usar PostgreSQL no Render, defina a variável DATABASE_URL
DATABASE_URL = env('DATABASE_URL', default=None)

if DATABASE_URL:
    # PostgreSQL via DATABASE_URL (Render, Heroku, etc.)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # SQLite para desenvolvimento local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings Básicas
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# NO CACHE - usando memória local simples
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = False  # Melhor performance
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Message Framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Email - Console Backend (apenas para desenvolvimento)
# Configure SMTP real depois se precisar
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging SIMPLIFICADO
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Configurações da aplicação - DESABILITADAS features pesadas
GARAGE_CONFIG = {
    'COMPANY_NAME': env('COMPANY_NAME', default='GarageRoute66'),
    'OS_PREFIX': env('OS_PREFIX', default='OS'),
    'AUTO_GENERATE_OS_NUMBER': True,
    'SEND_EMAIL_NOTIFICATIONS': False,  # Desabilitado
    'SEND_SMS_NOTIFICATIONS': False,    # Desabilitado
    'ENABLE_REPORTS': False,            # Sem PDF por enquanto
}

# Paginação
PAGINATE_BY = 20
