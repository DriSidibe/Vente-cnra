
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


# ==================================================
# PROFIL UTILISATEUR ET AUTHENTIFICATION
# ==================================================

class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    api_key_expiration_datetime = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'


# ==================================================
# GESTION DES PRODUITS
# ==================================================

class Produit(models.Model):

    nom = models.CharField(
        max_length=150
    )

    reference = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    categorie = models.CharField(
        max_length=100
    )

    prix_achat = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    prix_vente = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    quantite = models.PositiveIntegerField(
        default=0
    )

    seuil_alerte = models.PositiveIntegerField(
        default=5
    )

    image = models.ImageField(
        upload_to='produits/',
        blank=True,
        null=True
    )

    date_ajout = models.DateTimeField(
        auto_now_add=True
    )

    date_modification = models.DateTimeField(
        auto_now=True
    )

    actif = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = 'produit'
        ordering = ['-date_ajout']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['categorie']),
            models.Index(fields=['actif']),
        ]

    def __str__(self):
        return f"{self.nom} ({self.reference})"


# ==================================================
# GESTION DES VENTES
# ==================================================

class Vente(models.Model):

    STATUT_CHOICES = [
        ('Payée', 'Payée'),
        ('En attente', 'En attente'),
        ('Annulée', 'Annulée'),
    ]

    PAIEMENT_CHOICES = [
        ('Espèces', 'Espèces'),
        ('Orange Money', 'Orange Money'),
        ('MTN Money', 'MTN Money'),
        ('Wave', 'Wave'),
        ('Virement bancaire', 'Virement bancaire'),
    ]

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='ventes'
    )

    client = models.CharField(
        max_length=150
    )

    date_vente = models.DateField(
        auto_now_add=True
    )

    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    paiement = models.CharField(
        max_length=50,
        choices=PAIEMENT_CHOICES
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='Payée'
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'vente'
        ordering = ['-date_creation']
        verbose_name = 'Vente'
        verbose_name_plural = 'Ventes'
        indexes = [
            models.Index(fields=['utilisateur', 'date_vente']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"Vente #{self.id} - {self.client}"


# ==================================================
# DÉTAILS DES VENTES
# ==================================================

class LigneVente(models.Model):

    vente = models.ForeignKey(
        Vente,
        on_delete=models.CASCADE,
        related_name='lignes'
    )

    produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,
        related_name='lignes_vente'
    )

    quantite = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    prix_unitaire = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    sous_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        db_table = 'ligne_vente'
        verbose_name = 'Ligne de vente'
        verbose_name_plural = 'Lignes de vente'

    def __str__(self):
        return (
            f"{self.produit.nom} - "
            f"{self.quantite} unité(s)"
        )
