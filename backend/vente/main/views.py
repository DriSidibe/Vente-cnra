from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from main.helpers import generateNewApiKey, isApiKeyExpired
from main.models import UserProfile
from .serializers.users_serializer import (
    ConnexionSerializer,
    InscriptionSerializer,
    UserProfileSerializer,
    UserSerializer,
)


def ouvrir_session(user):
    profil, _ = UserProfile.objects.get_or_create(user=user)
    if isApiKeyExpired(profil):
        generateNewApiKey(profil)
    return UserProfileSerializer(profil).data


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def connexion(request):
    serializer = ConnexionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': "Le nom d'utilisateur et le mot de passe sont requis"}, status=400)

    user = authenticate(request, **serializer.validated_data)
    if user is None:
        return Response({'error': "Nom d'utilisateur ou mot de passe incorrect"}, status=401)

    return Response(ouvrir_session(user))


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def inscription(request):
    serializer = InscriptionSerializer(data=request.data)
    if not serializer.is_valid():
        messages = [str(message) for liste in serializer.errors.values() for message in liste]
        return Response({'error': ' '.join(messages)}, status=400)

    with transaction.atomic():
        donnees = ouvrir_session(serializer.save())
    return Response(donnees, status=201)


@api_view(['POST'])
def deconnexion(request):
    profil = request.auth
    profil.api_key = None
    profil.api_key_expiration_datetime = None
    profil.save()
    return Response({'message': 'Déconnexion réussie'})


@api_view(['GET'])
def moi(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
def users(request):
    return Response(UserSerializer(User.objects.order_by('id'), many=True).data)
