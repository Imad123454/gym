from django.utils.deprecation import MiddlewareMixin
from .models import Tenant

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(":")[0]
        try:
            tenant = Tenant.objects.get(domain=host)
            request.tenant = tenant
        except Tenant.DoesNotExist:
            request.tenant = None
