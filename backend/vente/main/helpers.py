import secrets
from datetime import timedelta

from django.utils import timezone

API_KEY_DUREE = timedelta(days=3)


def isApiKeyExpired(userProfile):
    if not userProfile.api_key or not userProfile.api_key_expiration_datetime:
        return True
    return userProfile.api_key_expiration_datetime <= timezone.now()


def generateNewApiKey(userProfile):
    userProfile.api_key = secrets.token_hex(32)
    userProfile.api_key_expiration_datetime = timezone.now() + API_KEY_DUREE
    userProfile.save()
    return userProfile
