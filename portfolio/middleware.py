from django.http import HttpResponseForbidden

from .models import BlockedVisitor
from .utils import get_client_ip


class BlockedVisitorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = get_client_ip(request)
        if (
            ip_address
            and BlockedVisitor.objects.filter(ip_address=ip_address).exists()
            and not getattr(request.user, 'is_staff', False)
        ):
            return HttpResponseForbidden('Access to this portfolio is blocked.')

        return self.get_response(request)
