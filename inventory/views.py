from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from admin_panel.models import ProductMaster, SuppMaster, Locations
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

from admin_panel.views import page
from inventory.models import PoHd


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


@login_required(login_url='/login/')
def purchasing(request):
    if PoHd.objects.all().count() > 0:
        page['title'] = "Purchase Order"
        context = {
            'page': page,
            'nav': True,
            'po': PoHd.objects.all().last().pk
        }
        return render(request, 'inventory/purchasing/view.html', context=context)
    else:
        return redirect('new_purchasing_order')


@login_required(login_url='/login/')
def new_purchasing_order(request):
    page['title'] = 'Creating Purchasing Order'
    context = {
        'page': page,
        'nav': True,
        'suppliers': SuppMaster.objects.all(),
        'locs': Locations.objects.all()
    }
    return render(request, 'inventory/purchasing/new.html', context=context)