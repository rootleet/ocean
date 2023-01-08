from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from admin_panel.models import ProductMaster, SuppMaster, Locations
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

from admin_panel.views import page
from inventory.form import NewAssetGroup, NewAsset
from inventory.models import PoHd, GrnHd, AssetGroup, Assets


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


@login_required(login_url='/login/')
def grn(request):
    if GrnHd.objects.all().count() > 0:
        page['title'] = "GRN"
        context = {
            'page': page,
            'nav': True,
            'entry': GrnHd.objects.all().last().pk
        }
        return render(request, 'inventory/grn/view.html', context=context)
    else:
        return redirect('new-grn')


@login_required(login_url='/login/')
def new_grn(request):
    page['title'] = 'Goods Receiving Note - NEW'
    context = {
        'page': page,
        'nav': True,
        'suppliers': SuppMaster.objects.all(),
        'locs': Locations.objects.all(),
        'po': PoHd.objects.filter(status=1)
    }
    return render(request, 'inventory/grn/new.html', context=context)


# assets
@login_required(login_url='/login/')
def assets(request):
    page['title'] = 'Assets'
    context = {
        'page': page,
        'nav': True,
        'suppliers': SuppMaster.objects.all(),
        'locs': Locations.objects.all(),
        'po': PoHd.objects.filter(status=1),
        'assgrp': AssetGroup.objects.all(),
        'assets':Assets.objects.all()
    }

    return render(request, 'inventory/assets/index.html', context=context)


def newgroup(request):
    if request.method == 'POST':
        form = NewAssetGroup(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accessories')
        else:
            return HttpResponse(form)


def assets_new(request):
    if request.method == 'POST':
        form = NewAsset(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('assets')
        else:
            return HttpResponse(form)
