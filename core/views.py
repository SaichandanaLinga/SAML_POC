from django.shortcuts import render, redirect
from django.contrib import auth
from djangosaml2.views import AssertionConsumerServiceView, LogoutInitView

def home(request):
    return render(request, 'home.html')

class DebugACSView(AssertionConsumerServiceView):
    def authenticate_user(self, request, session_info, attribute_mapping,
                         create_unknown_user, assertion_info):
        print("=" * 60)
        print("SESSION INFO:", session_info)
        print("AVA (attributes):", session_info.get('ava'))
        name_id = session_info.get('name_id')
        print("NAME ID TEXT:", name_id.text if name_id else "NONE")
        print("=" * 60)
        return super().authenticate_user(
            request, session_info, attribute_mapping,
            create_unknown_user, assertion_info
        )

class SafeLogoutView(LogoutInitView):
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            print(f"SAML Logout error (safe fallback): {e}")
            auth.logout(request)
            return redirect('/')