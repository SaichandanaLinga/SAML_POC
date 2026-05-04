# core/backends.py
import re
from social_core.backends.azuread import AzureADOAuth2
from social_core.backends.google import GoogleOAuth2
from social_core.exceptions import AuthForbidden

# UUID pattern — used to detect Azure Tenant IDs vs plain domain names
_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)


class SessionAwareAzureADOAuth2(AzureADOAuth2):
    """
    Azure AD OAuth2 backend that:
    - Reads client_id/client_secret from session (thread-safe multi-tenant)
    - Restricts login to a specific Azure AD tenant when oauth_allowed_domain is set
      (prevents users from other organizations logging in)
    """

    SESSION_KEY_MAP = {
        'KEY':    'azure_client_id',
        'SECRET': 'azure_client_secret',
    }

    def setting(self, name, default=None):
        if name in self.SESSION_KEY_MAP:
            try:
                val = self.strategy.request.session.get(self.SESSION_KEY_MAP[name])
                if val:
                    return val
            except AttributeError:
                pass
        return super().setting(name, default=default)

    @property
    def tenant_id(self):
        """
        If the IdP has an allowed domain/tenant set, lock the OAuth flow to that
        tenant only. Azure will then reject logins from other organizations.
        Falls back to 'common' (any Microsoft account) if not set.
        """
        try:
            tenant = self.strategy.request.session.get('azure_tenant_id')
            if tenant:
                return tenant
        except AttributeError:
            pass
        return 'common'

    def auth_complete(self, *args, **kwargs):
        response = super().auth_complete(*args, **kwargs)
        return response

    def get_user_details(self, response):
        details = super().get_user_details(response)

        allowed_domain = self.strategy.request.session.get('oauth_allowed_domain', '').lstrip('@')
        if not allowed_domain:
            return details

        # If oauth_allowed_domain is a UUID, it's a Tenant ID — the tenant_id
        # property already locked the OAuth URL to that tenant so Azure enforced
        # the restriction before the user even logged in. No email check needed.
        if _UUID_RE.match(allowed_domain):
            return details

        # If it's a plain domain name (e.g. acme.com), enforce via email check.
        # This is the post-login safety net in case tenant_id='common' is used.
        email = details.get('email') or response.get('upn', '')
        if not email.lower().endswith(f'@{allowed_domain.lower()}'):
            raise AuthForbidden(
                self,
                f"Login denied: only @{allowed_domain} accounts are allowed."
            )
        return details


class SessionAwareGoogleOAuth2(GoogleOAuth2):
    """
    Google OAuth2 backend that:
    - Reads client_id/client_secret from session (thread-safe multi-tenant)
    - Restricts login to a specific Google Workspace domain (hd parameter)
      when oauth_allowed_domain is set, e.g. 'acme.com'
    """

    SESSION_KEY_MAP = {
        'KEY':    'google_client_id',
        'SECRET': 'google_client_secret',
    }

    def setting(self, name, default=None):
        if name in self.SESSION_KEY_MAP:
            try:
                val = self.strategy.request.session.get(self.SESSION_KEY_MAP[name])
                if val:
                    return val
            except AttributeError:
                pass
        return super().setting(name, default=default)

    def auth_extra_arguments(self):
        """
        Pass the 'hd' (hosted domain) parameter to Google's authorization URL.
        This makes Google's login screen only show accounts from that domain
        AND Google enforces it server-side — not just a UI hint.
        """
        extra = super().auth_extra_arguments()
        try:
            allowed_domain = self.strategy.request.session.get('oauth_allowed_domain', '').lstrip('@')
            if allowed_domain:
                extra['hd'] = allowed_domain
        except AttributeError:
            pass
        return extra

    def get_user_details(self, response):
        details = super().get_user_details(response)

        # Second layer of enforcement: verify the returned token's hd claim
        # (defends against a crafted response bypassing the hd= URL parameter)
        allowed_domain = self.strategy.request.session.get('oauth_allowed_domain', '').lstrip('@')
        if allowed_domain:
            # Google sets 'hd' in the ID token for Workspace accounts
            token_hd = response.get('hd', '')
            email = details.get('email', '')
            domain_match = (
                token_hd.lower() == allowed_domain.lower() or
                email.lower().endswith(f'@{allowed_domain.lower()}')
            )
            if not domain_match:
                raise AuthForbidden(
                    self,
                    f"Login denied: only @{allowed_domain} accounts are allowed."
                )
        return details
