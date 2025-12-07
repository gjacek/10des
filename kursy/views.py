from django.shortcuts import render
from django.http import HttpResponse

def begin(request):
    return HttpResponse("Hello world!")

def login_view(request):
    """
    Widok logowania - strona główna aplikacji.
    Renderuje formularz logowania z integracją Alpine.js.
    """
    return render(request, 'registration/login.html')