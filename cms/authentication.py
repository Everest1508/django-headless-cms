"""
Custom authentication classes for the CMS API
"""
from rest_framework import authentication, exceptions
from .models import APIToken


class APITokenAuthentication(authentication.BaseAuthentication):
    """
    Custom token authentication using APIToken model.
    
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:
    
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    
    keyword = 'Token'
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        try:
            auth_type, token_key = auth_header.split(' ', 1)
        except ValueError:
            return None
        
        if auth_type.lower() != self.keyword.lower():
            return None
        
        try:
            token = APIToken.objects.select_related('user').get(key=token_key, is_active=True)
        except APIToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')
        
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        
        # Update last_used timestamp
        from django.utils import timezone
        APIToken.objects.filter(pk=token.pk).update(last_used=timezone.now())
        
        return (token.user, token)
    
    def authenticate_header(self, request):
        return self.keyword


