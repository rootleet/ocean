from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from reports.models import ReportLegend


@login_required()
def index(request):
    context = {
        'nav': True,
        'legends': ReportLegend.objects.all()
    }
    return render(request, 'reports/index.html', context=context)


@login_required()
def designer(request):
    context = {
        'nav': True
    }
    return render(request, 'reports/form-desinger.html', context=context)
