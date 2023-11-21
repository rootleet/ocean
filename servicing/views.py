from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

from admin_panel.models import UserAddOns, TicketHd
from servicing.models import Services, ServiceCard

context = {
    'nav': True,
    'page': {
        'title': "Service Center"
    }
}


# BASE
@login_required()
def base(request):
    return render(request, 'servicing/landing.html', context=context)


# services
@login_required()
def services(request):
    sers = Services.objects.filter(status=1)
    context['newcode'] = f"SERV{Services.objects.all().count() + 1}"
    context['services'] = sers
    context['page']['title'] = "Services"
    return render(request, 'servicing/services.html', context=context)


@login_required()
def newjob(request):
    sers = Services.objects.filter(status=1)
    if sers.count() < 1:
        messages.error(request, "Please Create A Service")
        return redirect('services')

    context['users'] = UserAddOns.objects.all()
    context['technicians'] = User.objects.filter(is_superuser=True)
    context['tickets'] = TicketHd.objects.filter(status=0)
    context['services'] = sers
    context['page']['title'] = "New Job Card"
    return render(request, 'servicing/new-job.html', context=context)


@login_required()
def jobcard(request):
    if ServiceCard.objects.all().count() < 1:
        return redirect('newjob')

    cardno = ServiceCard.objects.filter(pk__gt=0).last().cardno
    context['page']['title'] = "Job Cards"
    context['cardno'] = cardno
    return render(request, 'servicing/jobcard.html', context=context)


@login_required()
def tracking(request, cardno):
    context['nav'] = True
    context['pagevalid'] = False
    context['pagemessage'] = "none"

    # check if user own this

    if ServiceCard.objects.filter(Q(cardno=cardno) | Q(task__uni=cardno)).exists():
        service = ServiceCard.objects.get(Q(cardno=cardno) | Q(task__uni=cardno))

        # validate owner
        if service.owner.pk == request.user.pk or request.user.is_superuser:
            context['pagevalid'] = True
            context['pagemessage'] = service
        else:
            context['pagemessage'] = "You are not the owner of this ticket"

    else:
        context['pagemessage'] = f"SERVICE with number {cardno} DOES NOT EXIST"

    return render(request, 'servicing/transactions.html', context=context)

@login_required()
def service(request, service_id):
    if Services.objects.filter(pk=service_id).exists():
        serv = Services.objects.get(pk=service_id)
        context['nav'] = True
        context['page']['title'] = f"{serv.name} Detail"
        context['service'] = serv
        context['jobs'] = ServiceCard.objects.filter(service=serv).order_by('-pk')[:10]
        context['job_counts'] = {
            'total': ServiceCard.objects.all().count(),
            'complete': ServiceCard.objects.filter(service=serv, status=2),
            'open': ServiceCard.objects.filter(service=serv,status=1)
        }

        return render(request, 'servicing/service.html', context=context)
    else:
        return HttpResponse(status=404)
