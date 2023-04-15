from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def base(request):
    return None

@login_required(login_url='/login/')
def carjobs(request):
    page = {
        'nav': True,
        'title': "Car Jobs"
    }

    context = {
        'page': page,
        'nav': True,
        'searchButton': 'carJob'
    }
    return render(request, 'cmms/car-jobs.html', context=context)
