from django.urls import path
from . import views


from django.urls import path, include


urlpatterns = [
    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('moi/', views.moi, name='moi'),
    path('users/', views.users, name='users'),
    path('produits/', views.produits, name='produits'),
    path('ajouter_produit/', views.ajouter_produit, name='ajouter_produit'),
    path('modifier_produit/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
    path('supprimer_produit/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),
    path('ventes/', views.ventes, name='ventes'),
    path('supprimer_vente/<int:vente_id>/', views.supprimer_vente, name='supprimer_vente'),
    path('statistiques_ventes/',views.statistiques_ventes,name='statistiques_ventes'),
    path('clients/', views.clients, name='clients'),
    path('ajouter_client/', views.ajouter_client, name='ajouter_client'),
    path('modifier_client/<int:client_id>/', views.modifier_client,name='modifier_client'),
    path('supprimer_client/<int:client_id>/',views.supprimer_client,name='supprimer_client'),
    path('stock/', views.stock, name='stock'),
    path('historique-stock/', views.historique_stock, name='historique_stock'),
    path('ajouter-mouvement-stock/', views.ajouter_mouvement_stock, name='ajouter_mouvement_stock'),
]
