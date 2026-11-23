from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, response


# Create your views here.
def dashbord(request):
    return render(request, "dashbord.html")
def connexion(request):

    if request.method == "POST":
        print(request.POST)
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None :
            login(request, user)
            return redirect("dashbord")

        return redirect("connexion")

       
    return render(request, "connexion.html")



def deconnexion(request):

    logout(request)

    messages.success(request, "Vous êtes déconnecté ! 👋")

    return redirect('connexion')

def test(request):
    return JsonResponse({"message": "ok"})