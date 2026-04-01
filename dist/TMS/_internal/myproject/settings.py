# myproject/settings.py  –  EXE-aware version
#
# REPLACE your existing settings.py with this file.
# It auto-detects whether it's running as a frozen EXE and
# adjusts all file-system paths accordingly.

import os
import sys
from pathlib import Path

# ── Path helpers ──────────────────────────────────────────────────────────────

def _resource(relative):
    """Path inside the PyInstaller bundle (_MEIPASS) or the project root."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(Path(__file__).resolve().parent.parent, relative)


def _writable(relative):
    """
    Path for *writable* data (DB, media, logs).
    When frozen: folder that contains the .exe
    When running normally: project root
    """
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), relative)
    return os.path.join(Path(__file__).resolve().parent.parent, relative)


BASE_DIR = Path(__file__).resolve().parent.parent

# ── Core ──────────────────────────────────────────────────────────────────────
SECRET_KEY = 'django-insecure-2^uld(+dc0i^2(x!=%4$571kz)4=b-qxu^p8qwhf%a$a!moeu+'
DEBUG = True
ALLOWED_HOSTS = ['*']

# ── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'myapp.apps.MyappConfig',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'myapp.middleware.CurrentUserMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

# ── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [_resource('myapp/templates')],  # ← bundle-aware
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myapp.context_processors.user_session',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _writable('db.sqlite3'),        # ← writable location
    }
}

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── i18n ──────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_URL = '/static/'

# Where collectstatic writes files (also bundled into the EXE)
STATIC_ROOT = _resource('staticfiles')

# Extra locations Django's staticfiles finder checks during development
STATICFILES_DIRS = []
_dev_static = str(BASE_DIR / 'static')
if os.path.isdir(_dev_static):
    STATICFILES_DIRS = [_dev_static]

# ── Media files ───────────────────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = _writable('media')          # ← writable location

# ── Misc ──────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django.server': {
            'handlers': ['null'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    },
    'handlers': {
        'null': {'class': 'logging.NullHandler'},
    },
}