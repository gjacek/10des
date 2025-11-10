from django.shortcuts import render
from django.http import HttpResponse

def begin(request):
    return HttpResponse("Hello world!")