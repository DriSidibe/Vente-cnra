
from rest_framework import serializers
from main.models import Produit, MouvementStock


class StockSerializer(serializers.ModelSerializer):
    statut_stock = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = [
            'id',
            'nom',
            'reference',
            'description',
            'categorie',
            'prix_achat',
            'prix_vente',
            'quantite',
            'seuil_alerte',
            'image',
            'actif',
            'statut_stock',
        ]

    def get_statut_stock(self, obj):
        if obj.quantite == 0:
            return 'Rupture'

        if obj.quantite <= obj.seuil_alerte:
            return 'Stock faible'

        return 'Disponible'


class MouvementStockSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(
        source='produit.nom',
        read_only=True
    )

    utilisateur_nom = serializers.CharField(
        source='utilisateur.username',
        read_only=True
    )

    class Meta:
        model = MouvementStock
        fields = [
            'id',
            'produit',
            'produit_nom',
            'type_mouvement',
            'quantite',
            'motif',
            'utilisateur',
            'utilisateur_nom',
            'date_mouvement',
        ]

        read_only_fields = [
            'id',
            'utilisateur',
            'date_mouvement',
        ]

    def validate_quantite(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "La quantité doit être supérieure à zéro."
            )

        return value
