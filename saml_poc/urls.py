# saml_poc/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.views import home, login_page, sso_login, DebugACSView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', home, name='home'),

    # Login page — shows all clients
    path('login/', login_page, name='login'),

    # Dynamic SSO entry point per client
    path('sso/login/<slug:slug>/', sso_login, name='sso_login'),

    # SAML endpoints
    path('saml2/acs/', DebugACSView.as_view(), name='saml2_acs'),
    path('saml2/', include('djangosaml2.urls')),

    # Google OAuth + Azure OAuth
    path('social-auth/', include('social_django.urls', namespace='social')),

    # Custom OIDC
    path('oidc/', include('mozilla_django_oidc.urls')),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)