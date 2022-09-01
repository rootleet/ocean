import os
import random
import string
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.sites import requests
from django.core.mail import send_mail
from stream.models import *

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    videos = Videos.objects.all()
    context = {
        'videos':videos
    }
    return render(request, 'streams/index.html', context=context)


def upload_video(request):
    import subprocess
    current_user = request.user
    if request.method == 'POST':
        form_date = request.POST
        file = request.FILES
        title = form_date['title']
        description = form_date['description']
        video_file = file['video_file']

        file_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        thumbnail = f'static/general/videos/{file_key}.jpg'

        try:
            Videos(key=file_key, file=video_file, title=title, descr=description).save()
            # get video details
            saved_file = Videos.objects.last()
            file_name = saved_file.file.path

            # return HttpResponse(file_name)

            img_output_path = Path(thumbnail).absolute()

            src_video_path = Path(file_name).absolute()

            command = f"ffmpeg -i \"{src_video_path}\" -ss 00:00:00.000 -vframes 1 \"{img_output_path}\""

            os.system(command)

            return HttpResponse("Done")
        except Exception as e:
            return HttpResponse(f"Could Not Add {e} {video_file}")


def watch(request, key):
    if Videos.objects.filter(key=key).exists():
        video = Videos.objects.get(key=key)
        context = {
            'video':video
        }
        return render(request, 'streams/watch.html', context=context)