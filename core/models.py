# core/models.py
from django.db import models

class IdentityProvider(models.Model):

    PROTOCOL_CHOICES = [
        ('saml', 'SAML 2.0'),
        ('google_oauth', 'Google OAuth 2.0'),
        ('azure_oauth', 'Microsoft Azure AD OAuth'),
        ('oidc', 'Custom OIDC / OAuth'),
    ]

    # ── Client Info ─────────────────────────────────────────
    client_name = models.CharField(max_length=100)
    slug = models.SlugField(
        unique=True,
        help_text="Used in login URL: /sso/login/<slug>/"
    )
    protocol = models.CharField(max_length=20, choices=PROTOCOL_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ── SAML Fields ─────────────────────────────────────────
    saml_metadata_file = models.FileField(
        upload_to='idp_metadata/',
        blank=True,
        null=True,
        help_text="Upload IdP metadata XML file (for SAML protocol)"
    )

    # ── OAuth Fields (Google / Azure) ────────────────────────
    oauth_client_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Client ID from Google Cloud Console or Azure Portal"
    )
    oauth_client_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="Client Secret from Google Cloud Console or Azure Portal"
    )

    # ── Custom OIDC Fields ───────────────────────────────────
    oidc_authorization_endpoint = models.URLField(
        blank=True,
        help_text="e.g. https://your-idp.com/oauth/authorize"
    )
    oidc_token_endpoint = models.URLField(
        blank=True,
        help_text="e.g. https://your-idp.com/oauth/token"
    )
    oidc_user_endpoint = models.URLField(
        blank=True,
        help_text="e.g. https://your-idp.com/oauth/userinfo"
    )
    oidc_jwks_endpoint = models.URLField(
        blank=True,
        help_text="e.g. https://your-idp.com/.well-known/jwks.json"
    )

    class Meta:
        verbose_name = "Identity Provider"
        verbose_name_plural = "Identity Providers"

    def __str__(self):
        return f"{self.client_name} ({self.get_protocol_display()})"