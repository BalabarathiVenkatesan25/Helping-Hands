from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse

class UserStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # 1. Enforce Suspension Check
            if not request.user.is_active:
                logout(request)
                messages.error(request, "Your account has been suspended. Please contact the administrator.")
                return redirect('login')

            # 2. Enforce Orphanage Approval Check
            if request.user.is_orphanage:
                profile = getattr(request.user, 'orphanage_profile', None)
                # If they have no profile, let them complete it or proceed, but if they have it and it's not approved:
                if profile and not profile.is_approved:
                    allowed_paths = [
                        reverse('logout'),
                        reverse('pending_approval'),
                    ]
                    # Check if requested path is allowed or starts with static/media
                    path = request.path
                    if path not in allowed_paths and not path.startswith('/static/') and not path.startswith('/media/'):
                        return redirect('pending_approval')

        response = self.get_response(request)
        return response
