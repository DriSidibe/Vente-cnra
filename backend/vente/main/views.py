
from uuid import uuid4
from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, F
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404

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
    MouvementStock,
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

from main.serializers.stock_serializer import (
    StockSerializer,
    MouvementStockSerializer,
)


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

    return Response(
        UserSerializer(request.user).data
    )


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
# CRÉER OU RETROUVER UN CLIENT
# Le formulaire de vente fournit uniquement le nom.
# ==================================================

def creer_ou_retrouver_client(nom_client):

    nom_client = str(nom_client).strip()

    if not nom_client:

        raise ValueError("Le nom du client est obligatoire.")

    # Rechercher un client portant déjà ce nom.
    client = User.objects.filter(
        last_name__iexact=nom_client,
        is_staff=False,
        is_superuser=False
    ).first()

    if client:

        return client

    # Créer un identifiant unique.
    username = f"client_{uuid4().hex[:12]}"

    # Créer le client avec uniquement son nom.
    client = User.objects.create_user(
        username=username,
        first_name="",
        last_name=nom_client,
        password=None
    )

    # Le compte créé automatiquement ne permet pas de se connecter.
    client.set_unusable_password()
    client.save()

    return client


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
# AFFICHER ET AJOUTER LES VENTES
# ==================================================

@api_view(['GET', 'POST'])
def ventes(request):

    # ==================================================
    # AFFICHER LES VENTES
    # ==================================================

    if request.method == 'GET':

        liste = Vente.objects.filter(
            utilisateur=request.user
        ).prefetch_related('lignes__produit')

        return Response([
            vente_en_json(vente)
            for vente in liste
        ])

    # ==================================================
    # RÉCUPÉRER LES DONNÉES
    # ==================================================

    donnees = request.data

    client = donnees.get('client')

    paiement = donnees.get('paiement')

    statut = donnees.get('statut', 'Payée')

    lignes = donnees.get('lignes', [])

    # Vérifier le nom du client.
    if not client or not str(client).strip():

        return Response({
            'error': 'Le nom du client est obligatoire'
        }, status=400)

    # Vérifier le mode de paiement.
    paiements_valides = [
        choix[0] for choix in Vente.PAIEMENT_CHOICES
    ]

    if paiement not in paiements_valides:

        return Response({
            'error': 'Mode de paiement invalide'
        }, status=400)

    # Vérifier le statut.
    statuts_valides = [
        choix[0] for choix in Vente.STATUT_CHOICES
    ]

    if statut not in statuts_valides:

        return Response({
            'error': 'Statut invalide'
        }, status=400)

    # Vérifier les lignes de vente.
    if not isinstance(lignes, list) or not lignes:

        return Response({
            'error': 'Ajoutez au moins un produit à la vente'
        }, status=400)

    try:

        with transaction.atomic():

            # ==================================================
            # CRÉER OU RETROUVER LE CLIENT
            # ==================================================

            client_nom = str(client).strip()

            client_obj = creer_ou_retrouver_client(client_nom)

            # ==================================================
            # CALCULER LE MONTANT TOTAL
            # ==================================================

            montant_total = Decimal('0.00')

            lignes_a_enregistrer = []

            for element in lignes:

                if not isinstance(element, dict):

                    raise ValueError(
                        'Données de produit invalides'
                    )

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

                    raise ValueError(
                        'Identifiant du produit manquant'
                    )

                # Récupérer le produit et verrouiller sa ligne.
                produit = Produit.objects.select_for_update().get(
                    id=produit_id,
                    actif=True
                )

                # Vérifier le stock si la vente est payée.
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

            # ==================================================
            # CRÉER LA VENTE ET LA LIER AU CLIENT
            # ==================================================

            vente = Vente.objects.create(

                utilisateur=request.user,

                client=client_nom,

                client_utilisateur=client_obj,

                paiement=paiement,

                statut=statut,

                montant_total=montant_total

            )

            # ==================================================
            # ENREGISTRER LES LIGNES DE VENTE
            # ==================================================

            for element in lignes_a_enregistrer:

                LigneVente.objects.create(

                    vente=vente,

                    produit=element['produit'],

                    quantite=element['quantite'],

                    prix_unitaire=element['prix'],

                    sous_total=element['sous_total']

                )

                # Diminuer le stock si la vente est payée.
                if statut == 'Payée':

                    produit = element['produit']

                    produit.quantite -= element['quantite']

                    produit.save(
                        update_fields=['quantite']
                    )

        # Retourner la vente créée.
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

            # Restaurer le stock si la vente est payée.
            if vente.statut == 'Payée':

                lignes = list(
                    vente.lignes.select_related('produit').all()
                )

                for ligne in lignes:

                    produit = Produit.objects.select_for_update().get(
                        id=ligne.produit_id
                    )

                    produit.quantite += ligne.quantite

                    produit.save(
                        update_fields=['quantite']
                    )

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


# ==================================================
# VÉRIFICATION DU DROIT ADMINISTRATEUR
# ==================================================

def verifier_administrateur(request):

    utilisateur = request.user

    return (
        utilisateur.is_authenticated
        and (
            utilisateur.is_staff
            or utilisateur.is_superuser
        )
    )


# ==================================================
# AFFICHER LES CLIENTS
# URL : /vente/clients/
# ==================================================

@api_view(['GET'])
def clients(request):

    if not verifier_administrateur(request):

        return Response({
            'error': "Accès réservé aux administrateurs."
        }, status=403)

    liste_clients = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).order_by('-id')

    serializer = ClientSerializer(
        liste_clients,
        many=True
    )

    return Response(serializer.data, status=200)


# ==================================================
# AJOUTER UN CLIENT
# URL : /vente/ajouter_client/
# ==================================================

@api_view(['POST'])
def ajouter_client(request):

    if not verifier_administrateur(request):

        return Response({
            'error': "Accès réservé aux administrateurs."
        }, status=403)

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


# ==================================================
# MODIFIER UN CLIENT
# URL : /vente/modifier_client/<id>/
# ==================================================

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


# ==================================================
# SUPPRIMER UN CLIENT
# URL : /vente/supprimer_client/<id>/
# ==================================================

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

    # Empêcher la suppression de son propre compte.
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
                'Ce client possède déjà des ventes ou des données liées. '
                'Désactivez son compte au lieu de le supprimer.'
            )

        }, status=409)

    except Exception as error:

        return Response({

            'error': 'Une erreur est survenue pendant la suppression.',

            'details': str(error)

        }, status=500)


# ==================================================
# AFFICHER LE STOCK
# URL : /vente/stock/
# ==================================================

@api_view(['GET'])
def stock(request):

    if not request.user.is_authenticated:

        return Response(
            {'error': 'Authentification requise.'},
            status=401
        )

    liste_produits = Produit.objects.filter(
        actif=True
    ).order_by('nom')

    serializer = StockSerializer(
        liste_produits,
        many=True
    )

    return Response(serializer.data, status=200)


# ==================================================
# HISTORIQUE DU STOCK
# URL : /vente/historique_stock/
# ==================================================

@api_view(['GET'])
def historique_stock(request):

    if not request.user.is_authenticated:

        return Response(
            {'error': 'Authentification requise.'},
            status=401
        )

    mouvements = MouvementStock.objects.select_related(
        'produit',
        'utilisateur'
    ).all()

    serializer = MouvementStockSerializer(
        mouvements,
        many=True
    )

    return Response(serializer.data, status=200)


# ==================================================
# AJOUTER UN MOUVEMENT DE STOCK
# URL : /vente/ajouter_mouvement_stock/
# ==================================================

@api_view(['POST'])
def ajouter_mouvement_stock(request):

    if not request.user.is_authenticated:

        return Response(
            {'error': 'Authentification requise.'},
            status=401
        )

    if not (
        request.user.is_staff
        or request.user.is_superuser
    ):

        return Response(
            {'error': 'Accès réservé aux administrateurs.'},
            status=403
        )

    serializer = MouvementStockSerializer(
        data=request.data
    )

    if not serializer.is_valid():

        return Response({

            'error': 'Informations invalides.',

            'details': serializer.errors

        }, status=400)

    produit_id = serializer.validated_data['produit'].id

    type_mouvement = serializer.validated_data['type_mouvement']

    quantite = serializer.validated_data['quantite']

    try:

        with transaction.atomic():

            produit = get_object_or_404(
                Produit.objects.select_for_update(),
                id=produit_id
            )

            if type_mouvement == 'SORTIE':

                if produit.quantite < quantite:

                    return Response({

                        'error': 'Stock insuffisant.',

                        'stock_disponible': produit.quantite

                    }, status=400)

                Produit.objects.filter(
                    pk=produit.pk
                ).update(
                    quantite=F('quantite') - quantite
                )

            elif type_mouvement == 'ENTREE':

                Produit.objects.filter(
                    pk=produit.pk
                ).update(
                    quantite=F('quantite') + quantite
                )

            else:

                return Response(
                    {'error': 'Type de mouvement invalide.'},
                    status=400
                )

            produit.refresh_from_db()

            mouvement = serializer.save(
                utilisateur=request.user
            )

        return Response({

            'message': 'Mouvement de stock enregistré avec succès.',

            'mouvement': MouvementStockSerializer(mouvement).data,

            'nouvelle_quantite': produit.quantite

        }, status=201)

    except Exception as error:

        return Response({

            'error': "Une erreur est survenue lors de l'opération.",

            'details': str(error)

        }, status=500)
