from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from appconfig.form import NewApp, NewVersion
from appscenter.models import AppsGroup, App, AppAssign, AppProviders
from blog.anton import make_md5


@login_required()
def index(request):
    import time

    username = request.user.username
    current_time = str(time.time())
    data = username + current_time
    provider_options = ''
    providers = AppProviders.objects.filter(is_active=True)
    for provider in providers:
        provider_options += f"<option value='{provider.pk}'>{provider.name}</option>"


    context = {
        'nav': True,
        'providers': AppProviders.objects.filter(is_active=True),
        'apps': App.objects.all(),
        'md': make_md5(data),
        'html':{
            'providers_options': provider_options
        }
    }

    return render(request, 'appcenter/index.html', context=context)


@login_required()
@csrf_exempt
def save_new_app(request):
    if request.method == 'POST':
        form = NewApp(request.POST, request.FILES)
        try:

            form.save()
            messages.success(request, "APP SAVED")
        except Exception as e:
            messages.error(request, e)
            return HttpResponse(form)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def app(request, pk):
    this_app = App.objects.get(pk=pk)
    assign = AppAssign.objects.filter(app=this_app)

    context = {
        'nav': True,
        'app': this_app,
        'next_version': this_app.version + 1,
        'assigns': assign
    }
    return render(request, 'appcenter/app.html', context=context)


@login_required()
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
