from django.urls import path

from main.views import vente_home


urlpatterns = [
    path('connexion/', vente_home),
]
