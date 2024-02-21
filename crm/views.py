from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from crm.models import Logs, CrmUsers


# Create your views here.
@login_required()
def base(request):
    context = {
        'nav': True,
        'page': {
            'title': "CRM",
        },
        'logs': Logs.objects.filter(owner=request.user,created_date=timezone.now().date()).order_by('-pk')
    }

    return render(request, 'crm/logs.html', context=context)


def crm_users(request):
    context = {
        'nav': True,
        'page': {
            'title': "CRM USERS",
        },
        'users': CrmUsers.objects.all().order_by('-pk')
    }

    return render(request, 'crm/crm-users.html', context=context)