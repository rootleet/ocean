from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse

from django.shortcuts import render, redirect

from appconfig.form import NewApp, NewVersion
from appscenter.models import AppsGroup, App, AppAssign


# Create your views here.
def index(request):
    context = {
        'nav': True,
        'appgroups': AppsGroup.objects.filter(status=1),
        'apps': App.objects.all()
    }

    return render(request, 'appcenter/index.html', context=context)


def save_new_app(request):
    if request.method == 'POST':
        form = NewApp(request.POST, request.FILES)

        try:

            form.save()
            messages.success(request, "APP SAVED")
        except Exception as e:
            messages.error(request, e)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def app(request, pk):
    this_app = App.objects.get(pk=pk)
    assign = AppAssign.objects.filter(app=this_app)
    context = {
        'nav': True,
        'app': this_app,
        'next_version': this_app.version + 1,
        'assigns':assign
    }
    return render(request, 'appcenter/app.html', context=context)


def save_app_update(request):
    # return HttpResponse("HELLo WORLD")
    if request.method == 'POST':
        form = NewVersion(request.POST, request.FILES)

        try:
            form.save()
            version = form.cleaned_data['version_no']
            appx = App.objects.get(pk=form.cleaned_data['app'].pk)
            appx.version = version
            appx.save()
            # return HttpResponse("DONE")
            messages.success(request, "VERSION SAVED")
        except Exception as e:
            # return HttpResponse(e)
            messages.error(request, e)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
