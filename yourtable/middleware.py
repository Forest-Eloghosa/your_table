import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class StaticRequestLoggingMiddleware(MiddlewareMixin):
    """Log requests for static files to help debug missing assets during development.

    This middleware prints INFO logs for requests whose path starts with '/static/'
    and returns without modifying the response.
    """

    def process_request(self, request):
        try:
            path = request.path
        except Exception:
            return None
        if path.startswith('/static/'):
            logger.info('Static request: %s %s', request.method, path)
        return None
