import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = bool(int(os.environ.get("DJANGO_DEBUG", 0)))

FRONTEND_URL = os.environ.get("FRONTEND_URL")
BACKEND_URL = os.environ.get("BACKEND_URL")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(',')

CORS_ALLOW_ALL_ORIGINS = True  # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000"
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000"
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'drf_yasg',
    'django_celery_results',
    'django_celery_beat',
    'simple_history',
    'core',
    'social_media',
    'subscription',
    'workspace',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_PATH, 'templates')],
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

WSGI_APPLICATION = 'app.wsgi.application'

if os.environ.get("IS_LOCAL"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("SQL_DATABASE_NAME"),
            "USER": os.environ.get("SQL_USER"),
            "PASSWORD": os.environ.get("SQL_PASSWORD"),
            "HOST": os.environ.get("SQL_HOST"),
            "PORT": os.environ.get("SQL_PORT"),
        },

    }

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_FROM = os.environ.get('EMAIL_FROM')
DEFAULT_FROM_EMAIL = EMAIL_FROM
LOGIN_REDIRECT_URL = os.environ.get('LOGIN_REDIRECT_URL')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
AUTH_USER_MODEL = 'core.User'
ACCOUNT_TEMPLATE_EXTENSION = "html"
ACCOUNT_EMAIL_CONFIRMATION_TEMPLATE = 'account/email/email_confirmation.html'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SIGNUP_REDIRECT_URL = '/'
ACCOUNT_EMAIL_VERIFICATION = 'optional'

EMAIL_CONFIRM_REDIRECT_BASE_URL = f"{FRONTEND_URL}/verify_registration/"
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = f"{FRONTEND_URL}/reset_password/"

REST_AUTH = {
    'LOGIN_SERIALIZER': 'core.serializers.CustomLoginSerializer',
    'REGISTER_SERIALIZER': 'core.serializers.CustomRegisterSerializer',
    'USER_DETAILS_SERIALIZER': 'core.serializers.CustomUserDetailsSerializer',
}

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'DEFAULT_API_URL': BACKEND_URL,
}

SUBSCRIPTION_SETTINGS = {
    "STRIPE_API_SECRET": os.environ.get("STRIPE_TEST_SECRET_KEY"),
    "STRIPE_WEBHOOK_SECRET": os.environ.get("DJSTRIPE_WEBHOOK_SECRET"),
    "FRONT_END_BASE_URL": FRONTEND_URL,
    "DJANGO_USER_EMAIL_FIELD": "email",
    "USER_CREATE_DEFAULTS_ATTRIBUTE_MAP": {"email": "email"},
    "NEW_USER_FREE_TRIAL_DAYS": 3,
}

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

FACEBOOK_APP_ID = os.environ.get("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.environ.get("FACEBOOK_APP_SECRET")
