class CustomFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # If this is a chat embed view, allow it to be framed
        if request.path.startswith('/ai_agent/chat/embed/'):
            # Remove the X-Frame-Options header if it exists
            if 'X-Frame-Options' in response:
                del response['X-Frame-Options']

            # Add a permissive Content-Security-Policy
            response['Content-Security-Policy'] = "frame-ancestors 'self' *"

        return response
class CustomFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # If this is a chat embed view, allow it to be framed
        if request.path.startswith('/ai_agent/chat/embed/'):
            # Remove the X-Frame-Options header if it exists
            if 'X-Frame-Options' in response:
                del response['X-Frame-Options']

            # Add a permissive Content-Security-Policy
            response['Content-Security-Policy'] = "frame-ancestors 'self' *"

        return response