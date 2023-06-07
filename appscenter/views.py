from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse

from django.shortcuts import render, redirect

from appconfig.form import NewApp, NewVersion
from appscenter.models import AppsGroup, App, AppAssign


@login_required()
# Create your views here.
def index(request):
    import hashlib
    import time

    # Assuming you have access to the `request` object with the user information
    username = request.user.username

    # Get the current time as a string
    current_time = str(time.time())

    # Concatenate the username and current time
    data = username + current_time

    # Create an MD5 hash object
    md5_hash = hashlib.md5()

    # Convert the data string to bytes
    data_bytes = data.encode('utf-8')

    # Update the MD5 hash object with the data bytes
    md5_hash.update(data_bytes)

    # Get the hexadecimal representation of the MD5 hash
    md5_hex = md5_hash.hexdigest()

    context = {
        'nav': True,
        'appgroups': AppsGroup.objects.filter(status=1),
        'apps': App.objects.all(),
        'md':md5_hex
    }

    return render(request, 'appcenter/index.html', context=context)


@login_required()
def save_new_app(request):
    if request.method == 'POST':
        form = NewApp(request.POST, request.FILES)
        try:

            form.save()
            messages.success(request, "APP SAVED")
        except Exception as e:
            messages.error(request, e)

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
