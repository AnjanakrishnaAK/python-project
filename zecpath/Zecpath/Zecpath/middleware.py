from django.http import JsonResponse

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Skip unauthenticated users
        if not user.is_authenticated:
            return self.get_response(request)

        # Block inactive users
        if not user.is_active:
            return JsonResponse(
                {"detail": "Account disabled"},
                status=403
            )

        return self.get_response(request)