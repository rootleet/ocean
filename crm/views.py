from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from crm.models import Logs, CrmUsers, FollowUp


# Create your views here.
@login_required()
def base(request):
    if request.user.is_superuser:
        logs = Logs.objects.filter(created_date=timezone.now().date()).order_by('-pk')
    else:
        logs = Logs.objects.filter(owner=request.user, created_date=timezone.now().date()).order_by('-pk')
    context = {
        'nav': True,
        'page': {
            'title': "CRM",
        },
        'logs': logs
    }

    return render(request, 'crm/logs.html', context=context)


def follows(request):
    if request.user.is_superuser:
        logs = FollowUp.objects.filter(is_open=True).order_by('-pk')
    else:
        logs = FollowUp.objects.filter(owner=request.user, is_open=True).order_by('-pk')
    context = {
        'nav': True,
        'page': {
            'title': "CRM Follow Up",
        },
        'logs': logs
    }

    return render(request, 'crm/follow.html', context=context)


def crm_users(request):
    context = {
        'nav': True,
        'page': {
            'title': "CRM USERS",
        },
        'users': CrmUsers.objects.all().order_by('-pk')
    }

    return render(request, 'crm/crm-users.html', context=context)


def crm_tools(request):
    context = {
        'nav': True,
        'page': {
            'title': "CRM TOOLS",
        },
        'users': CrmUsers.objects.all().order_by('-pk')
    }

    return render(request, 'crm/crm-tools.html', context=context)
