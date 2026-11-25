from django.urls import path
from . import views


urlpatterns = [
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('dashbord/', views.dashbord, name='dashbord'),
    path('users/', views.users, name='users'),
]