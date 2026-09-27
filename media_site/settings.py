from pathlib import Path
from decouple import config
from django.contrib.messages import constants as messages_const

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="fallback-key-change-in-production")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost",
    cast=lambda value: [host.strip() for host in value.split(",") if host.strip()],
)
SITE_URL = config("SITE_URL", default="").rstrip("/")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_ckeditor_5",
    "apps.core",
    "apps.articles",
    "apps.accounts",
    "apps.contact",
    "apps.comments",
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

ROOT_URLCONF = "media_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings_processor",
                "apps.articles.context_processors.categories_processor",
                "apps.articles.context_processors.journalist_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "media_site.wsgi.application"

# ─── MySQL / XAMPP ────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME", default="media_site"),
        "USER": config("DB_USER", default="root"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default="3306", cast=int),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
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

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "America/Port-au-Prince"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "fr",
        "toolbar": {
            "items": [
                "heading",
                "|",
                "bold",
                "italic",
                "underline",
                "link",
                "bulletedList",
                "numberedList",
                "blockQuote",
                "|",
                "undo",
                "redo",
            ]
        },
    }
}

LOGIN_URL = "/comptes/connexion/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-media-cache",
    }
}

# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="").strip()
EMAIL_HOST_PASSWORD = "".join(config("EMAIL_HOST_PASSWORD", default="").split())
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER or "webmaster@localhost"
)

if DEBUG and not (EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

ARTICLES_PER_PAGE = 9

MESSAGE_TAGS = {
    messages_const.DEBUG: "debug",
    messages_const.INFO: "info",
    messages_const.SUCCESS: "success",
    messages_const.WARNING: "warning",
    messages_const.ERROR: "danger",
}
