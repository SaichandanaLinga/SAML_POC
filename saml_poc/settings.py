# settings.py
from pathlib import Path
from saml2_config import SAML_CONFIG
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = "django-insecure-(7lhdl^29jxs1nng@1hwst9h!ouvp_tefr((ixxlp=&1ux)@83"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "djangosaml2",
    "social_django",            # Google OAuth + Azure OAuth
    "mozilla_django_oidc",      # Custom OIDC
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "djangosaml2.middleware.SamlSessionMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",            # Django admin login
    "djangosaml2.backends.Saml2Backend",                    # SAML (any IdP)
    "social_core.backends.google.GoogleOAuth2",             # Google OAuth
    "social_core.backends.azuread.AzureADOAuth2",           # Microsoft OAuth
    "mozilla_django_oidc.auth.OIDCAuthenticationBackend",   # Custom OIDC
]

SITE_ID = 1

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ── SAML Settings ──────────────────────────────────────────
SAML_CONFIG = SAML_CONFIG
SAML_USE_NAME_ID_AS_USERNAME = True
SAML_CREATE_UNKNOWN_USER = True
SAML_IGNORE_LOGOUT_ERRORS = True
SAML_CSP_HANDLER = ""
SAML_ATTRIBUTE_MAPPING = {
    # Google Workspace SAML
    'email': ('email',),
    'firstName': ('first_name',),
    'lastName': ('last_name',),
    # Azure AD SAML
    'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress': ('email',),
    'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname': ('first_name',),
    'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname': ('last_name',),
    # Generic
    'uid': ('username',),
}

# ── Google OAuth Settings ──────────────────────────────────
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = os.getenv(
    'SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI'
)

# ── Azure AD OAuth Settings ────────────────────────────────
SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = ''          # Fill when client provides
SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = ''       # Fill when client provides

# ── Custom OIDC Settings ───────────────────────────────────
OIDC_RP_CLIENT_ID = ''                       # Fill when client provides
OIDC_RP_CLIENT_SECRET = ''                   # Fill when client provides
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_OP_AUTHORIZATION_ENDPOINT = ''
OIDC_OP_TOKEN_ENDPOINT = ''
OIDC_OP_USER_ENDPOINT = ''
OIDC_OP_JWKS_ENDPOINT = ''

# ── CSRF ───────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'https://sneezing-overhung-overlaid.ngrok-free.dev',
]

ROOT_URLCONF = "saml_poc.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'core' / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",    # OAuth
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "saml_poc.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_DB_PORT", "5432"),
        "NAME": os.environ.get("POSTGRES_DB_NAME", "saml_poc"),
        "USER": os.environ.get("POSTGRES_DB_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_DB_PASSWORD", "password"),
    }
}

# File uploads (IdP metadata files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"