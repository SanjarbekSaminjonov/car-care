import os
from pathlib import Path

from environs import Env

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
VAR_DIR = ROOT_DIR / "var"

env = Env()
env.read_env()

SETTINGS_MODULE = os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.local")

SECRET_KEY = env.str("DJANGO_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS: list[str] = []
CSRF_TRUSTED_ORIGINS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.users.apps.UsersConfig",
    "apps.telegram.apps.TelegramConfig",
    "apps.cars.apps.CarsConfig",
    "apps.odometer.apps.OdometerConfig",
    "apps.maintenance.apps.MaintenanceConfig",
    "apps.audit.apps.AuditConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.assistant.apps.AssistantConfig",
    "apps.webapp.apps.WebAppConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST", default="localhost"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
        "CONN_MAX_AGE": env.int("POSTGRES_CONN_MAX_AGE", default=60),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = VAR_DIR / "static"
STATICFILES_DIRS = [SRC_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = VAR_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"
TEST_RUNNER = "config.test_runner.SrcDiscoverRunner"

LOG_LEVEL = env.str("DJANGO_LOG_LEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(module)s:%(lineno)d %(message)s",
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] %(levelname)s [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

FILE_UPLOAD_MAX_MEMORY_SIZE = env.int(
    "DJANGO_FILE_UPLOAD_MAX_MEMORY_SIZE", default=5 * 1024 * 1024
)
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int(
    "DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE", default=5 * 1024 * 1024
)

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

AI_ASSISTANT_ENABLED = env.bool("AI_ASSISTANT_ENABLED", default=False)
AI_ASSISTANT_PROVIDER = env.str("AI_ASSISTANT_PROVIDER", default="openai-compatible")
AI_ASSISTANT_API_KEY = env.str("AI_ASSISTANT_API_KEY", default="")
AI_ASSISTANT_BASE_URL = env.str(
    "AI_ASSISTANT_BASE_URL",
    default="https://api.openai.com/v1",
)
AI_ASSISTANT_MODEL = env.str("AI_ASSISTANT_MODEL", default="gpt-4o-mini")
AI_ASSISTANT_TIMEOUT_SECONDS = env.int("AI_ASSISTANT_TIMEOUT_SECONDS", default=30)
AI_ASSISTANT_MAX_CONTEXT_RECORDS = env.int("AI_ASSISTANT_MAX_CONTEXT_RECORDS", default=5)

TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_WEBAPP_URL = env.str("TELEGRAM_WEBAPP_URL", default="")
TELEGRAM_WEBAPP_AUTH_MAX_AGE_SECONDS = env.int(
    "TELEGRAM_WEBAPP_AUTH_MAX_AGE_SECONDS",
    default=86400,
)
