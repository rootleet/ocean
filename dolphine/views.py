from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def dolphine(request):
    return render(request, 'dolphine/landing.html')
