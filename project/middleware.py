from django.conf import settings
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        login_url = settings.LOGIN_URL
        static_url = settings.STATIC_URL if settings.STATIC_URL.startswith('/') else '/' + settings.STATIC_URL
        media_url = settings.MEDIA_URL if settings.MEDIA_URL.startswith('/') else '/' + settings.MEDIA_URL

        if request.user.is_authenticated:
            return self.get_response(request)

        if path.startswith(static_url) or path.startswith(media_url):
            return self.get_response(request)

        if path.startswith('/admin/') or path.startswith('/accounts/'):
            return self.get_response(request)

        if path == login_url:
            return self.get_response(request)

        return redirect(f'{login_url}?next={request.path}')
