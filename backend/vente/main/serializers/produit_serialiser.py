from main.models import Produit
from rest_framework import serializers  

class ProduitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Produit
        fields = "__all__"
