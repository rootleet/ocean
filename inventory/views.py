from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from admin_panel.models import ProductMaster
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required



# Create your views here.

@login_required(login_url='/login/')
def inventory(request):
    if ProductMaster.objects.filter().count() < 1:
        # redirect to new products creation
        messages.error(request, f"done%%Inventory is empty, Create an item")
        return redirect('new-product')
    context = {
        'nav': True,
        'page_title': 'Inventory | View', 'products': ProductMaster.objects.all()
    }
    return render(request, 'dashboard/products/view.html', context=context)


def purchasing(request):
    return HttpResponse("HELLO WORLD")
