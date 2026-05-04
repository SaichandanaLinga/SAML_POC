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
    "core.backends.SessionAwareGoogleOAuth2",               # Google OAuth  (reads creds from session)
    "core.backends.SessionAwareAzureADOAuth2",              # Microsoft OAuth (reads creds from session)
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

# Allow a social account already in the DB to log back in instead of raising
# AuthAlreadyAssociated when the same account is used across sessions.
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',       # finds existing association
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',    # links account to user
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# ── Azure AD OAuth Settings ────────────────────────────────
# No static KEY/SECRET here — credentials are stored per-request in the session
# by sso_login() and read by SessionAwareAzureADOAuth2 backend in core/backends.py
SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = ''
SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = ''
# Force the correct public-facing callback URL (needed when running behind ngrok/reverse proxy)
SOCIAL_AUTH_AZUREAD_OAUTH2_CALLBACK_URL = 'https://sneezing-overhung-overlaid.ngrok-free.dev/social-auth/complete/azuread-oauth2/'

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

# Trust the ngrok reverse proxy so request.build_absolute_uri() returns
# the correct public URL instead of 127.0.0.1
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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