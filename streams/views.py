import os
import random
import string
from pathlib import Path
from django.templatetags.static import static

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.sites import requests
from django.core.mail import send_mail
from streams.models import *

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    videos = Videos.objects.all()
    context = {
        'videos': videos
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
        thumbnail = f'/home/stuffs/Development/pythonProjects/ocean/static/general/videos/{file_key}.jpg'

        try:
            Videos(key=file_key, file=video_file, title=title, descr=description).save()
            # get video details
            saved_file = Videos.objects.last()
            file_name = saved_file.file.path

            from pyffmpeg import FFmpeg
            import subprocess
            subprocess.call(
                ['ffmpeg', '-i', f"/home/stuffs/Development/pythonProjects/ocean/{static(file_name)}", '-ss',
                 '00:00:5.000', '-vframes', '1', thumbnail])
            # ff = FFmpeg()
            # ff.convert(static(file_name), thumbnail)

            import cv2
            x_file = file_name
            img_output_path = Path(f"{static('../static/general/videos/')}").absolute()

            src_video_path = Path(x_file).absolute()

            command = f"ffmpeg -i \"{file_name}\" -ss 00:00:10 -vframes 1 -f " \
                      f"image2 \"{thumbnail}\" "

            os.system(command)

            # return HttpResponse(f"PATH :: {file_name} | | THUMB :: {thumbnail}")
            return HttpResponse('done%%')

        except Exception as e:
            return HttpResponse(f"Could Not Add {e} {video_file}")


def watch(request,key):
    if Videos.objects.filter(key=key).exists():

        return render(request,'streams/watch.html',context={'video':Videos.objects.get(key=key)})