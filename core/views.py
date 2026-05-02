# core/views.py
from django.shortcuts import render, redirect
from django.contrib import auth
from django.conf import settings
from djangosaml2.views import AssertionConsumerServiceView
from .models import IdentityProvider
from saml2_config import get_saml_config
from saml2.config import SPConfig
from saml2.metadata import entity_descriptor
import saml2


def home(request):
    return render(request, 'home.html')


def login_page(request):
    """
    Shows all available IdP login options.
    Each active client gets a login button.
    """
    idps = IdentityProvider.objects.filter(is_active=True)
    error = request.GET.get('error', '')
    return render(request, 'login.html', {
        'idps': idps,
        'error': error
    })


def sso_login(request, slug):
    """
    Dynamic SSO login entry point.
    /sso/login/acme-corp/  → loads Acme Corp's IdP config
    /sso/login/beta-inc/   → loads Beta Inc's IdP config

    Checks protocol and routes to:
      - SAML  → /saml2/login/
      - Google OAuth → Google consent screen
      - Azure OAuth  → Microsoft consent screen
      - Custom OIDC  → OIDC authorization endpoint
    """
    try:
        idp = IdentityProvider.objects.get(slug=slug, is_active=True)
    except IdentityProvider.DoesNotExist:
        return redirect('/login/?error=invalid_idp')

    # ── SAML Protocol ──────────────────────────────────────
    if idp.protocol == 'saml':
        if not idp.saml_metadata_file:
            return redirect('/login/?error=missing_metadata')

        # Load this client's SAML config dynamically
        saml_config = get_saml_config(idp.saml_metadata_file.path)
        conf = SPConfig()
        conf.load(saml_config)

        # Store in Django settings at runtime so djangosaml2 uses it
        settings.SAML_CONFIG = saml_config

        # Store client slug in session for reference after ACS
        request.session['current_idp_slug'] = slug
        request.session['current_idp_name'] = idp.client_name

        return redirect('/saml2/login/')

    # ── Google OAuth Protocol ──────────────────────────────
    elif idp.protocol == 'google_oauth':
        # Load this client's OAuth credentials into settings at runtime
        settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = idp.oauth_client_id
        settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = idp.oauth_client_secret

        request.session['current_idp_slug'] = slug
        request.session['current_idp_name'] = idp.client_name

        return redirect('/social-auth/login/google-oauth2/')

    # ── Azure AD OAuth Protocol ────────────────────────────
    elif idp.protocol == 'azure_oauth':
        # Load this client's Azure credentials into settings at runtime
        settings.SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = idp.oauth_client_id
        settings.SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = idp.oauth_client_secret

        request.session['current_idp_slug'] = slug
        request.session['current_idp_name'] = idp.client_name

        return redirect('/social-auth/login/azuread-oauth2/')

    # ── Custom OIDC Protocol ───────────────────────────────
    elif idp.protocol == 'oidc':
        # Load OIDC endpoints into settings at runtime
        settings.OIDC_RP_CLIENT_ID = idp.oauth_client_id
        settings.OIDC_RP_CLIENT_SECRET = idp.oauth_client_secret
        settings.OIDC_OP_AUTHORIZATION_ENDPOINT = idp.oidc_authorization_endpoint
        settings.OIDC_OP_TOKEN_ENDPOINT = idp.oidc_token_endpoint
        settings.OIDC_OP_USER_ENDPOINT = idp.oidc_user_endpoint
        settings.OIDC_OP_JWKS_ENDPOINT = idp.oidc_jwks_endpoint

        request.session['current_idp_slug'] = slug
        request.session['current_idp_name'] = idp.client_name

        return redirect('/oidc/authenticate/')

    return redirect('/login/?error=unsupported_protocol')


class DebugACSView(AssertionConsumerServiceView):
    """
    Custom ACS view that prints what IdP sends.
    Keep this for debugging — remove in production.
    """
    def authenticate_user(self, request, session_info, attribute_mapping,
                         create_unknown_user, assertion_info):
        print("=" * 60)
        print(f"CLIENT: {request.session.get('current_idp_name', 'Unknown')}")
        print("SESSION INFO:", session_info)
        name_id = session_info.get('name_id')
        print("NAME ID:", name_id.text if name_id else "NONE")
        print("AVA (attributes):", session_info.get('ava'))
        print("=" * 60)

        return super().authenticate_user(
            request, session_info, attribute_mapping,
            create_unknown_user, assertion_info
        )