
from uuid import uuid4
from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from main.helpers import generateNewApiKey, isApiKeyExpired
from main.models import (
    Produit,
    UserProfile,
    Vente,
    LigneVente,
)

from .serializers.users_serializer import (
    ConnexionSerializer,
    InscriptionSerializer,
    UserProfileSerializer,
    UserSerializer,
)

from .serializers.produit_serialiser import ProduitSerializer
from .serializers.vente_serializer import VenteSerializer
from main.serializers.client_serializer import ClientSerializer
from django.shortcuts import get_object_or_404


# ==================================================
# AUTHENTIFICATION
# ==================================================

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
        return Response({
            'error': "Le nom d'utilisateur et le mot de passe sont requis"
        }, status=400)

    user = authenticate(request, **serializer.validated_data)

    if user is None:
        return Response({
            'error': "Nom d'utilisateur ou mot de passe incorrect"
        }, status=401)

    return Response(ouvrir_session(user))


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def inscription(request):
    serializer = InscriptionSerializer(data=request.data)

    if not serializer.is_valid():
        messages = [
            str(message)
            for liste in serializer.errors.values()
            for message in liste
        ]

        return Response({
            'error': ' '.join(messages)
        }, status=400)

    with transaction.atomic():
        donnees = ouvrir_session(serializer.save())

    return Response(donnees, status=201)


@api_view(['POST'])
def deconnexion(request):
    profil = request.auth

    profil.api_key = None
    profil.api_key_expiration_datetime = None
    profil.save()

    return Response({
        'message': 'Déconnexion réussie'
    })


@api_view(['GET'])
def moi(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
def users(request):
    utilisateurs = User.objects.order_by('id')

    return Response(
        UserSerializer(utilisateurs, many=True).data
    )


# ==================================================
# GESTION DES PRODUITS
# ==================================================

@api_view(['GET'])
def produits(request):
    liste = Produit.objects.order_by('id')

    return Response(
        ProduitSerializer(liste, many=True).data
    )


@api_view(['POST'])
def ajouter_produit(request):
    donnees = request.data.copy()

    donnees['reference'] = "PROD" + str(uuid4())[:5].upper()

    serializer = ProduitSerializer(data=donnees)

    if not serializer.is_valid():
        messages = [
            str(message)
            for liste in serializer.errors.values()
            for message in liste
        ]

        return Response({
            'error': ' '.join(messages)
        }, status=400)

    with transaction.atomic():
        produit = serializer.save()

    return Response(
        ProduitSerializer(produit).data,
        status=201
    )


@api_view(['PUT'])
def modifier_produit(request, produit_id):
    try:
        produit = Produit.objects.get(id=produit_id)

    except Produit.DoesNotExist:
        return Response({
            'error': 'Produit non trouvé'
        }, status=404)

    serializer = ProduitSerializer(
        produit,
        data=request.data,
        partial=True
    )

    if not serializer.is_valid():
        messages = [
            str(message)
            for liste in serializer.errors.values()
            for message in liste
        ]

        return Response({
            'error': ' '.join(messages)
        }, status=400)

    with transaction.atomic():
        produit = serializer.save()

    return Response(
        ProduitSerializer(produit).data,
        status=200
    )


@api_view(['DELETE'])
def supprimer_produit(request, produit_id):
    try:
        produit = Produit.objects.get(id=produit_id)

    except Produit.DoesNotExist:
        return Response({
            'error': 'Produit non trouvé'
        }, status=404)

    with transaction.atomic():
        produit.delete()

    return Response({
        'message': 'Produit supprimé avec succès'
    })


# ==================================================
# FORMATAGE DES VENTES EN JSON
# ==================================================

def vente_en_json(vente):
    lignes = []

    for ligne in vente.lignes.select_related('produit').all():
        lignes.append({
            'id': ligne.id,
            'produit_id': ligne.produit.id,
            'produit': ligne.produit.nom,
            'reference': ligne.produit.reference,
            'quantite': ligne.quantite,
            'prix_unitaire': str(ligne.prix_unitaire),
            'sous_total': str(ligne.sous_total),
        })

    return {
        'id': vente.id,
        'client': vente.client,
        'date': vente.date_vente.isoformat(),
        'montant': str(vente.montant_total),
        'paiement': vente.paiement,
        'statut': vente.statut,
        'lignes': lignes,
    }


# ==================================================
# AJOUTER ET AFFICHER LES VENTES
# ==================================================

@api_view(['GET', 'POST'])
def ventes(request):

    # AFFICHER LES VENTES
    if request.method == 'GET':

        liste = Vente.objects.filter(
            utilisateur=request.user
        ).prefetch_related('lignes__produit')

        return Response([
            vente_en_json(vente)
            for vente in liste
        ])

    # CRÉER UNE VENTE
    donnees = request.data

    client = donnees.get('client')
    paiement = donnees.get('paiement')
    statut = donnees.get('statut', 'Payée')
    lignes = donnees.get('lignes', [])

    if not client or not str(client).strip():
        return Response({
            'error': 'Le nom du client est obligatoire'
        }, status=400)

    paiements_valides = [
        choix[0] for choix in Vente.PAIEMENT_CHOICES
    ]

    statuts_valides = [
        choix[0] for choix in Vente.STATUT_CHOICES
    ]

    if paiement not in paiements_valides:
        return Response({
            'error': 'Mode de paiement invalide'
        }, status=400)

    if statut not in statuts_valides:
        return Response({
            'error': 'Statut invalide'
        }, status=400)

    if not isinstance(lignes, list) or not lignes:
        return Response({
            'error': 'Ajoutez au moins un produit à la vente'
        }, status=400)

    try:
        with transaction.atomic():

            montant_total = Decimal('0.00')
            lignes_a_enregistrer = []

            # VÉRIFIER LES PRODUITS ET LES QUANTITÉS
            for element in lignes:

                if not isinstance(element, dict):
                    raise ValueError('Données de produit invalides')

                produit_id = element.get('produit_id')

                try:
                    quantite = int(element.get('quantite', 0))
                except (ValueError, TypeError):
                    raise ValueError('Quantité invalide')

                if quantite <= 0:
                    raise ValueError(
                        'La quantité doit être supérieure à zéro'
                    )

                if not produit_id:
                    raise ValueError('Identifiant du produit manquant')

                produit = Produit.objects.select_for_update().get(
                    id=produit_id,
                    actif=True
                )

                # VÉRIFIER LE STOCK SI LA VENTE EST PAYÉE
                if statut == 'Payée' and produit.quantite < quantite:
                    raise ValueError(
                        f'Stock insuffisant pour {produit.nom}. '
                        f'Stock disponible : {produit.quantite}'
                    )

                prix = produit.prix_vente
                sous_total = prix * quantite

                montant_total += sous_total

                lignes_a_enregistrer.append({
                    'produit': produit,
                    'quantite': quantite,
                    'prix': prix,
                    'sous_total': sous_total,
                })

            # CRÉER LA VENTE
            vente = Vente.objects.create(
                utilisateur=request.user,
                client=str(client).strip(),
                paiement=paiement,
                statut=statut,
                montant_total=montant_total
            )

            # ENREGISTRER LES LIGNES DE VENTE
            for element in lignes_a_enregistrer:

                LigneVente.objects.create(
                    vente=vente,
                    produit=element['produit'],
                    quantite=element['quantite'],
                    prix_unitaire=element['prix'],
                    sous_total=element['sous_total']
                )

                # DIMINUER LE STOCK SI LA VENTE EST PAYÉE
                if statut == 'Payée':
                    produit = element['produit']
                    produit.quantite -= element['quantite']

                    produit.save(update_fields=['quantite'])

        return Response(
            vente_en_json(vente),
            status=201
        )

    except Produit.DoesNotExist:
        return Response({
            'error': 'Un produit sélectionné est introuvable ou inactif'
        }, status=404)

    except (ValueError, TypeError, InvalidOperation, ArithmeticError) as erreur:
        return Response({
            'error': str(erreur)
        }, status=400)


# ==================================================
# SUPPRIMER UNE VENTE
# ==================================================

@api_view(['DELETE'])
def supprimer_vente(request, vente_id):

    try:
        with transaction.atomic():

            vente = Vente.objects.select_for_update().get(
                id=vente_id,
                utilisateur=request.user
            )

            # RESTAURER LE STOCK SI LA VENTE EST PAYÉE
            if vente.statut == 'Payée':

                lignes = list(
                    vente.lignes.select_related('produit').all()
                )

                for ligne in lignes:

                    produit = Produit.objects.select_for_update().get(
                        id=ligne.produit_id
                    )

                    produit.quantite += ligne.quantite

                    produit.save(update_fields=['quantite'])

            vente.delete()

        return Response({
            'message': 'Vente supprimée avec succès'
        })

    except Vente.DoesNotExist:
        return Response({
            'error': 'Vente introuvable'
        }, status=404)


# ==================================================
# STATISTIQUES DES VENTES
# ==================================================

@api_view(['GET'])
def statistiques_ventes(request):

    queryset = Vente.objects.filter(
        utilisateur=request.user
    )

    total_ventes = queryset.count()

    chiffre_affaires = queryset.filter(
        statut='Payée'
    ).aggregate(
        total=Sum('montant_total')
    )['total'] or Decimal('0.00')

    ventes_en_attente = queryset.filter(
        statut='En attente'
    ).count()

    ventes_payees = queryset.filter(
        statut='Payée'
    ).count()

    return Response({
        'total_ventes': total_ventes,
        'chiffre_affaires': str(chiffre_affaires),
        'ventes_en_attente': ventes_en_attente,
        'ventes_validees': ventes_payees,
    })



# ==========================================
# VÉRIFICATION DU DROIT ADMINISTRATEUR
# ==========================================

def verifier_administrateur(request):

    utilisateur = request.user

    return (
        utilisateur.is_authenticated
        and (
            utilisateur.is_staff
            or utilisateur.is_superuser
        )
    )


# ==========================================
# AFFICHER ET AJOUTER LES CLIENTS
# URL : /vente/clients/
# ==========================================

@api_view(['GET', 'POST'])
def clients(request):

    if not verifier_administrateur(request):
        return Response({
            'error': "Accès réservé aux administrateurs."
        }, status=403)

    # AFFICHER LES CLIENTS
    if request.method == 'GET':

        liste_clients = User.objects.filter(
            is_staff=False,
            is_superuser=False
        ).order_by('-id')

        serializer = ClientSerializer(
            liste_clients,
            many=True
        )

        return Response(serializer.data, status=200)

    # AJOUTER UN CLIENT
@api_view(['POST'])
def ajouter_client(request):
    serializer = ClientSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response({
            'error': 'Veuillez vérifier les informations du client.',
            'details': serializer.errors
        }, status=400)

    try:
        with transaction.atomic():

            nouveau_client = serializer.save()

            # Créer son profil pour la gestion de l'API Key.
            UserProfile.objects.get_or_create(
                user=nouveau_client
            )

        return Response({
            'message': 'Client ajouté avec succès.',
            'client': ClientSerializer(nouveau_client).data
        }, status=201)

    except Exception as error:
        return Response({
            'error': "Une erreur est survenue lors de l'ajout du client.",
            'details': str(error)
        }, status=500)


# ==========================================
# MODIFIER UN CLIENT
# URL : /vente/modifier_client/<id>/
# ==========================================

@api_view(['PUT', 'PATCH'])
def modifier_client(request, client_id):

    if not verifier_administrateur(request):
        return Response({
            'error': "Accès réservé aux administrateurs."
        }, status=403)

    client = get_object_or_404(
        User,
        id=client_id,
        is_staff=False,
        is_superuser=False
    )

    serializer = ClientSerializer(
        client,
        data=request.data,
        partial=True
    )

    if not serializer.is_valid():
        return Response({
            'error': 'Impossible de modifier ce client.',
            'details': serializer.errors
        }, status=400)

    try:
        with transaction.atomic():
            client = serializer.save()

        return Response({
            'message': 'Client modifié avec succès.',
            'client': ClientSerializer(client).data
        }, status=200)

    except Exception as error:
        return Response({
            'error': 'Une erreur est survenue pendant la modification.',
            'details': str(error)
        }, status=500)


# ==========================================
# SUPPRIMER UN CLIENT
# URL : /vente/supprimer_client/<id>/
# ==========================================

@api_view(['DELETE'])
def supprimer_client(request, client_id):

    if not verifier_administrateur(request):
        return Response({
            'error': "Accès réservé aux administrateurs."
        }, status=403)

    client = get_object_or_404(
        User,
        id=client_id,
        is_staff=False,
        is_superuser=False
    )

    # Empêcher l'administrateur de supprimer son propre compte.
    if client.id == request.user.id:
        return Response({
            'error': 'Vous ne pouvez pas supprimer votre propre compte.'
        }, status=400)

    try:
        with transaction.atomic():
            client.delete()

        return Response({
            'message': 'Client supprimé avec succès.'
        }, status=200)

    except ProtectedError:
        return Response({
            'error': (
                'Ce client possède déjà des ventes. '
                'Désactivez son compte au lieu de le supprimer.'
            )
        }, status=409)

    except Exception as error:
        return Response({
            'error': 'Une erreur est survenue pendant la suppression.',
            'details': str(error)
        }, status=500)
