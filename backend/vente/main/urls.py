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
]
