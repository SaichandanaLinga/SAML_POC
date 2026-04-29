from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import home, DebugACSView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('saml2/acs/', DebugACSView.as_view(), name='saml2_acs'),
    path('saml2/', include('djangosaml2.urls')),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]