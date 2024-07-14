from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from admin_panel.models import PackingMaster, ProductGroup, ProductGroupSub, ProductMaster, SuppMaster, Locations, \
    TaxMaster, UnitMembers, UserAddOns, TransferHD
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

from admin_panel.views import page
from appscenter.models import App
from inventory.form import NewAssetGroup, NewAsset, NewWorkstation
from inventory.models import PoHd, GrnHd, AssetGroup, Assets, WorkStation, Computer


# Create your views here.

@login_required(login_url='/login/')
def inventory(request):
    if ProductMaster.objects.filter().count() < 1:
        # redirect to new products creation
        messages.error(request, f"done%%Inventory is empty, Create an item")
        return redirect('new-product')
    product = ProductMaster.objects.filter().last()
    context = {
        'nav': True,
        'page_title': 'Inventory | View',
        'barcode': product.barcode
    }
    return render(request, 'dashboard/products/prodctMaster.html', context=context)
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
        'po': PoHd.objects.filter(status=1, open=1)
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
        'assets': Assets.objects.all()
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
        form = NewAsset(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('assets')
        else:
            return HttpResponse(form)


@login_required(login_url='/login/')
def workstation(request):
    page['title'] = 'Workstation'
    context = {
        'page': page,
        'nav': True,
        'suppliers': SuppMaster.objects.all(),
        'locs': Locations.objects.all(),
        'mems': UnitMembers.objects.all(),
        'assets': Assets.objects.filter(type=1),
        'wst': WorkStation.objects.all(),

    }

    return render(request, 'inventory/workstation/index.html', context=context)


def save_workstation(request):
    if request.method == 'POST':
        form = NewWorkstation(request.POST)
        if form.is_valid():
            form.save()
            return redirect('workstation')
        else:
            return HttpResponse(form)

@login_required(login_url='/login/')
def view_workstation(request, mac_addr):
    page['title'] = 'Workstation'
    apps = App.objects.all()

    if Computer.objects.filter(mac_address=mac_addr).exists():
        device = Computer.objects.get(mac_address=mac_addr)
        
        context = {
            'page': page,
            'nav': True,
            'apps': apps,
            'dev': device,
            'users':UserAddOns.objects.all()

        }
        return render(request, 'inventory/workstation/view.html', context=context)
    else:
        return redirect('workstation')

@login_required(login_url='/login/')
def new_products(request):
    groups = ProductGroup.objects.filter(status=1)
    taxes = TaxMaster.objects.filter(status=1)
    packs = PackingMaster.objects.filter(status=1)
    supps = SuppMaster.objects.filter(status=1)

    if groups.count() < 1:
        messages.error(request, "done%%Create groups before you can add products")
        return redirect('inventory_tools')

    if supps.count() < 1:
        messages.error(request, "done%%Create or enable at least one supplier before you can add products")
        return redirect('inventory_tools')

    if ProductGroupSub.objects.filter(status=1).count() < 1:
        messages.error(request, "done%%Create or enable at least one sub group before you can add products")
        return redirect('inventory_tools')

    if taxes.count() < 1:
        messages.error(request, "done%%Create or enable at least one tax group before you can add products")
        return redirect('inventory_tools')

    if packs.count() < 1:
        messages.error(request, "done%%Create or enable at least one packaging before you can add products")
        return redirect('inventory_tools')

    context = {
        'nav': True,
        'page_title': 'Products Master | New',
        'groups': groups, 'taxes': taxes, 'packs': packs, 'supps': supps
    }
    return render(request, 'dashboard/products/newV2.html', context=context)
    return render(request,'dashboard/products/new.html',context=context)
    return render(request,'inventory/product/new.html',context=context)

@login_required()
def transfer(request):
    if TransferHD.objects.all().count() > 0:
        last_transfer = TransferHD.objects.all().last()
        page['title'] = 'Transfers'

        context = {
            'page': page,
            'nav': True,
            'locs':Locations.objects.all(),
            'last_transfer': last_transfer.pk,

        }

        return render(request, 'inventory/transfer/view.html', context=context)
    else:
        return redirect('new_transfer')


def transfer_new(request):
    page['title'] = 'New Transfers'

    context = {
        'page': page,
        'nav': True,
        'locs': Locations.objects.all()

    }

    return render(request, 'inventory/transfer/new.html', context=context)