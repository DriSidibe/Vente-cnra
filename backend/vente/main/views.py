from django.shortcuts import render, redirect
# Create your views here.
def vente_home(request):
    return render(request, 'connexion.html')