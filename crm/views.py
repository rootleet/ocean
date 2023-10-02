from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from crm.models import Logs


# Create your views here.
@login_required()
def base(request):
    context = {
        'nav': True,
        'page': {
            'title': "CRM",
        },
        'logs': Logs.objects.filter(owner=request.user).order_by('-pk')
    }

    return render(request, 'crm/logs.html', context=context)
