
from rest_framework import serializers
from main.models import Vente, LigneVente


class LigneVenteSerializer(serializers.ModelSerializer):

    produit_id = serializers.IntegerField(
        source='produit.id',
        read_only=True
    )

    produit = serializers.CharField(
        source='produit.nom',
        read_only=True
    )

    reference = serializers.CharField(
        source='produit.reference',
        read_only=True
    )

    class Meta:
        model = LigneVente
        fields = [
            'id',
            'produit_id',
            'produit',
            'reference',
            'quantite',
            'prix_unitaire',
            'sous_total',
        ]


class VenteSerializer(serializers.ModelSerializer):

    date = serializers.DateField(
        source='date_vente',
        read_only=True
    )

    montant = serializers.DecimalField(
        source='montant_total',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    lignes = LigneVenteSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Vente
        fields = [
            'id',
            'client',
            'date',
            'montant',
            'paiement',
            'statut',
            'lignes',
        ]
