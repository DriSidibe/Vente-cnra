from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    api_key_expiration_datetime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username



    

class Produit(models.Model):

    nom = models.CharField(max_length=150)

    reference = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    categorie = models.CharField(max_length=100)

    prix_achat = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    prix_vente = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    quantite = models.PositiveIntegerField(default=0)

    seuil_alerte = models.PositiveIntegerField(default=5)

    image = models.ImageField(
        upload_to='produits/',
        blank=True,
        null=True
    )

    date_ajout = models.DateTimeField(auto_now_add=True)

    date_modification = models.DateTimeField(auto_now=True)

    actif = models.BooleanField(default=True)

    class Meta:
        db_table = 'produit'
        ordering = ['-date_ajout']

    def __str__(self):
        return self.nom
