from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from main.helpers import isApiKeyExpired
from main.models import UserProfile


class ApiKeyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None

        profil = UserProfile.objects.select_related('user').filter(api_key=api_key).first()
        if profil is None or isApiKeyExpired(profil) or not profil.user.is_active:
            raise AuthenticationFailed('Session invalide ou expirée')

        return profil.user, profil

    def authenticate_header(self, request):
        # Nécessaire pour que DRF réponde 401 (et non 403)
        return 'X-API-Key'
