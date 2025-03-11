from django.shortcuts import redirect
from django.urls import reverse

from src import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):   
        if not request.user.is_authenticated and settings.AUTHENTICATION_REQUIRED:
            excluded_exact_paths = ['/'] # This exact path does not require authentication
            excluded_paths = ['/media/', '/login', '/accounts', '/payment', '/legal'] # Paths starting with these do not require authentication
            if request.path not in excluded_exact_paths and not any([request.path.startswith(path) for path in excluded_paths]):
                return redirect(f"{reverse('login')}?next={request.path}")
        return self.get_response(request)
