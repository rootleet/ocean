from django.contrib.auth.decorators import login_required
from django.shortcuts import render



@login_required()
def index(request):
    context = {
        'nav':True
    }
    return render(request,'reports/index.html',context=context)
