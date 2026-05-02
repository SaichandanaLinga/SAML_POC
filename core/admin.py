# core/admin.py
from django.contrib import admin
from .models import IdentityProvider

@admin.register(IdentityProvider)
class IdentityProviderAdmin(admin.ModelAdmin):
    list_display = [
        'client_name', 'slug', 'protocol', 'is_active', 'created_at'
    ]
    list_filter = ['protocol', 'is_active']
    search_fields = ['client_name', 'slug']
    prepopulated_fields = {'slug': ('client_name',)}

    # Show relevant fields based on protocol
    fieldsets = (
        ('Client Info', {
            'fields': ('client_name', 'slug', 'protocol', 'is_active')
        }),
        ('SAML Configuration', {
            'fields': ('saml_metadata_file',),
            'description': 'Fill this section if protocol is SAML 2.0',
            'classes': ('collapse',),
        }),
        ('OAuth Configuration (Google / Azure)', {
            'fields': ('oauth_client_id', 'oauth_client_secret'),
            'description': 'Fill this section if protocol is Google OAuth or Azure OAuth',
            'classes': ('collapse',),
        }),
        ('Custom OIDC Configuration', {
            'fields': (
                'oidc_authorization_endpoint',
                'oidc_token_endpoint',
                'oidc_user_endpoint',
                'oidc_jwks_endpoint',
            ),
            'description': 'Fill this section if protocol is Custom OIDC',
            'classes': ('collapse',),
        }),
    )