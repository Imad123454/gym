"""
Django settings for gms project.
"""

from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================
# SECURITY
# ==============================

SECRET_KEY = "django-insecure-change-this"

DEBUG = True

ALLOWED_HOSTS = ["*"]


# ==============================
# INSTALLED APPS
# ==============================

INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your App
    'gmsapp',   # <==== CHANGE THIS TO YOUR APP NAME

    # Third Party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'rest_framework.authtoken'
]


# ==============================
# MIDDLEWARE
# ==============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # CORS
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gmsapp.middleware.TenantMiddleware',  # multi-tenancy

]


ROOT_URLCONF = 'gms.urls'


# ==============================
# TEMPLATES
# ==============================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # optional
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


WSGI_APPLICATION = 'gms.wsgi.application'


# ==============================
# DATABASE (MYSQL)
# ==============================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "fit",        # database name
        "USER": "root",          # your MySQL user
        "PASSWORD": "imad1234",          # your MySQL password
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


# ==============================
# CUSTOM USER MODEL
# ==============================

AUTH_USER_MODEL = "gmsapp.User"  # <==== IMPORTANT


# ==============================
# PASSWORD VALIDATION
# ==============================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# ==============================
# INTERNATIONALIZATION
# ==============================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"   # <=== India time

USE_I18N = True

USE_TZ = False


# ==============================
# STATIC & MEDIA
# ==============================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static"
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ==============================
# REST FRAMEWORK CONFIG
# ==============================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


# ==============================
# JWT SETTINGS
# ==============================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}


# ==============================
# CORS
# ==============================

CORS_ALLOW_ALL_ORIGINS = True


# ==============================
# DEFAULT PK TYPE
# ==============================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ----------------razzo keys ------------------
RAZORPAY_KEY_ID = "rzp_test_RbzD1hPaC6PQIy"
RAZORPAY_KEY_SECRET = "R4LCFHgkLu5KPyhdyLn9YI7l"
RAZORPAY_WEBHOOK_SECRET = "KLEcK25CqeD96@k"
