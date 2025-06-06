from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that gets JWT token from cookies instead of
    the Authorization header.
    """
    
    def authenticate(self, request):
        # Get the token from the cookie instead of the header
        access_token = request.COOKIES.get('access_token')
        
        if not access_token:
            return None
            
        # Validate CSRF for enhanced security (optional but recommended)
        self.enforce_csrf(request)
            
        # Use the token for authentication
        validated_token = self.get_validated_token(access_token)
        user = self.get_user(validated_token)
        
        return (user, validated_token)
    
    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for cookie-based authentication.
        Only needed for browser-based clients.
        """
        check = CSRFCheck(request)
        # The check is successfully performed when the method returns None
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
