from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from maintenance.models import Maintenance


@login_required()
def landing_page(request):
    context = {

        'nav': True,
        'maintenance':Maintenance.objects.all().order_by('-id')
    }
    return render(request, 'maintenance/landing.html', context=context)

@login_required()
def maintenance(request,uni):
    context = {

        'nav': True,
        'maintenance': Maintenance.objects.get(pk=uni)
    }
    return render(request, 'maintenance/maintenance.html', context=context)

@login_required()
def asset_groups(request):
    context = {
        'nav':True
    }
    return render(request,'maintenance/asset-groups.html',context=context)