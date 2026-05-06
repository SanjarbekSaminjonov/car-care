from django.core.exceptions import ImproperlyConfigured
from environs import EnvError

from config.settings.base import *  # noqa: F403,F401

try:
    ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
    CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS")
except EnvError as exc:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS va DJANGO_CSRF_TRUSTED_ORIGINS majburiy."
    ) from exc

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS production muhitida bo'sh bo'lmasligi kerak."
    )
if not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        "DJANGO_CSRF_TRUSTED_ORIGINS production muhitida bo'sh bo'lmasligi kerak."
    )

try:
    env.str("DJANGO_SECRET_KEY")
    env.str("POSTGRES_DB")
    env.str("POSTGRES_USER")
    env.str("POSTGRES_PASSWORD")
    env.str("POSTGRES_HOST")
    env.int("POSTGRES_PORT")
except EnvError as exc:
    raise ImproperlyConfigured(
        "Production uchun majburiy env o'zgaruvchilari yetishmayapti."
    ) from exc

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
USE_X_FORWARDED_HOST = env.bool("DJANGO_USE_X_FORWARDED_HOST", default=True)
SESSION_COOKIE_AGE = env.int("DJANGO_SESSION_COOKIE_AGE", default=60 * 60 * 24 * 14)
