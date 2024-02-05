from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import Locations
from maintenance.models import *


@login_required()
def landing_page(request):
    if Maintenance.objects.all().count() < 1:
        return redirect('new_maintain')
    context = {

        'nav': True,
        'page':{
            'title':"Work Request"
        },
        'maintenance': Maintenance.objects.filter(pk__gt=0).last()
    }
    return render(request, 'maintenance/landing.html', context=context)


@login_required()
def maintenance(request, uni):
    context = {

        'nav': True,
        'maintenance': Maintenance.objects.get(pk=uni)
    }
    return render(request, 'maintenance/maintenance.html', context=context)


@login_required()
def asset_groups(request):
    context = {
        'nav': True
    }
    return render(request, 'maintenance/asset-groups.html', context=context)


@login_required()
def assets(request):
    if MaintenanceAsset.objects.all().count() < 1:
        return redirect('new_maintenance_asset')
    context = {
        'nav': True,
        'last': MaintenanceAsset.objects.all().last()
    }
    return render(request, 'maintenance/asset.html', context=context)


@login_required()
def new_maintenance_asset(request):
    context = {
        'nav': True,
        'groups': MaintenanceAssetGroup.objects.filter(is_active=True).order_by('name'),
        'locations': Locations.objects.all().order_by('descr')
    }
    return render(request, 'maintenance/new-asset.html', context=context)


@login_required()
@csrf_exempt
def upload_asset_image(request):
    if request.method == 'POST':
        pk = request.POST['pk']
        file = request.FILES['image']

        asset = MaintenanceAsset.objects.get(pk=pk)
        asset.image = file
        asset.save()
        return redirect('maint_assets')


@login_required()
def new_maintain(request):
    doc_ini = "MT24-"
    entry_no = f"{doc_ini}{Maintenance.objects.all().count() + 1}"
    context = {
        'nav': True,
        'entry_no': entry_no,
        
        'assets': MaintenanceAsset.objects.all().order_by('location')
    }
    return render(request, 'maintenance/new-maintain.html', context=context)

@login_required()
@csrf_exempt
def upload_evidence(request):
    if request.method == 'POST':
        entry_no = request.POST['entry_no']
        file = request.FILES['evidence']

        asset = Maintenance.objects.get(entry_no=entry_no)
        asset.evidence = file
        asset.save()
        return redirect('maintenance')
    
@login_required()
def work_order(request):
    context = {
        'nav':True,
        'page':{
            'title':"Word Order"
        },
        'wo':WorkOrder.objects.all().last()
    }
    return render(request,'maintenance/work-order.html',context=context)

@login_required()
@csrf_exempt
def upload_wo_attachment(request):
    if request.method == 'POST':
        try:
            wo_att_no = request.POST['wo_att_no']
            wo = WorkOrder.objects.get(wo_no=wo_att_no)
            type = request.POST['type']
            file = request.FILES['file']
            description = request.POST['wo_att_descr']

            WordOrderAttachments(
                wo=wo,type=type,description=description,
                file = file,
                owner=request.user
            ).save()
            reponse = {
                'status_code':200,
                'message':wo.pk
            }
        except Exception as e:
            reponse = {
                'status_code':505,
                'message':str(e)
            }

        
        return JsonResponse(reponse, safe=False)
    
@login_required()
def wo_tracing(request,wo_no):
    if WorkOrder.objects.filter(wo_no=wo_no).exists():
        wo = WorkOrder.objects.get(wo_no=wo_no)
        context = {
            'nav':True,
            'page':{
                'title':"WOrk Order Tracking"
            },
            'wo':wo
        }
        return render(request,'maintenance/wo-tacking.html',context=context)
    else:
        return redirect('work_order')
    
@login_required()
def save_trans(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            details = request.POST.get('details')
            evidence_file = request.FILES.get('evidence')
            wo_pk = request.POST.get('wo')
            wo = WorkOrder.objects.get(wo_no=wo_pk)

            tran = WordOrderTransactions(title=title,description=details)
            tran.owner = request.user
            tran.wo=wo
            

            # Check if a file was uploaded
            if evidence_file:
                tran.evidence = evidence_file
            
            tran.save()
            reponse = {
                'status_code':200,
                'message':"Saved"
            }
        except Exception as e:
            reponse = {
                'status_code':505,
                'message':str(e)
            }

        return JsonResponse(reponse, safe=False)