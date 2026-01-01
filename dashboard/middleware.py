from django.utils.deprecation import MiddlewareMixin
from .models import UserAction
import re
from django.urls import resolve, Resolver404

class UserActionMiddleware(MiddlewareMixin):
    """
    Middleware to log user actions.
    """
    
    def process_response(self, request, response):
        # Only log actions for authenticated users
        if not request.user.is_authenticated:
            return response
            
        # Skip admin URLs
        if request.path.startswith('/admin/'):
            return response
            
        # Skip static files
        if request.path.startswith('/static/'):
            return response
            
        # Get the action type based on the request method and path
        action_type = self._get_action_type(request)
        
        # Skip if no action type determined
        if not action_type:
            return response
            
        # Try to get model name and record ID from the URL
        model_name, record_id = self._get_model_info(request)
        
        # Create the user action record
        UserAction.objects.create(
            user=request.user,
            action_type=action_type,
            model_name=model_name,
            record_id=record_id,
            details=f"URL: {request.path}, Method: {request.method}",
            ip_address=self._get_client_ip(request)
        )
        
        return response
    
    def _get_action_type(self, request):
        """Determine the action type based on the request method and path."""
        method = request.method
        path = request.path
        
        # Login/logout actions
        if path == '/accounts/login/' and method == 'POST':
            return 'login'
        if path == '/accounts/logout/':
            return 'logout'
            
        # CRUD actions based on HTTP method
        if method == 'GET':
            # Skip list views for 'view' action to reduce noise
            if re.search(r'/\d+/$', path):  # Detail view pattern
                return 'view'
        elif method == 'POST':
            if '/new/' in path or path.endswith('/create/'):
                return 'create'
            elif '/edit/' in path or '/update/' in path:
                return 'update'
            elif '/delete/' in path:
                return 'delete'
        
        # Default to 'other' for unrecognized patterns
        return 'other'
    
    def _get_model_info(self, request):
        """Extract model name and record ID from the URL if possible."""
        try:
            # Resolve the URL to get the view function
            resolver_match = resolve(request.path)
            
            # Get the model name from the view name if possible
            view_name = resolver_match.url_name
            if view_name:
                # Extract model name from view name patterns like 'resource-detail'
                model_match = re.match(r'([a-z-]+)-(?:detail|update|delete)', view_name)
                if model_match:
                    model_name = model_match.group(1).replace('-', '_')
                else:
                    model_name = None
            else:
                model_name = None
            
            # Get record ID from URL kwargs if available
            record_id = resolver_match.kwargs.get('pk')
            
            return model_name, record_id
        except Resolver404:
            return None, None
    
    def _get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip