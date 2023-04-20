import hashlib
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from dolphine.models import Files
from django.utils import timezone
from cryptography.fernet import Fernet


# Create your views here.
@login_required(login_url='/login/')
def dolphine(request):
    context = {
        'files': Files.objects.filter(owner=request.user)
    }
    return render(request, 'dolphine/landing.html', context=context)


@csrf_exempt
@login_required(login_url='/login/')
def upload(request):
    global resp
    if request.method == 'POST':
        try:
            data = {'message': [], 'status': 'success'}
            files = request.FILES.getlist('file[]')
            for file in files:
                size = file.size
                # Generate encryption string with timestamp, filename, and file size
                timestamp = str(timezone.now().timestamp()).encode()
                filename = file.name.encode()
                filesize = file.size
                encryption_string = timestamp + filename
                filename, extension = os.path.splitext(file.name)

                # Encrypt the encryption string using Fernet
                key = Fernet.generate_key()
                f = Fernet(key)
                encrypted_string = f.encrypt(encryption_string)
                hash_object = hashlib.md5(encrypted_string.decode().encode())
                hash_hex = hash_object.hexdigest()
                Files(file=file, enc=hash_hex, size=filesize, type=extension, owner=request.user).save()

                file_url = f"/dolphine/view/{hash_hex}/"
            resp = "FILE UPLOADED"

        except Exception as e:
            resp = e

    return HttpResponse(resp)


@login_required(login_url='/login/')
def delete(request, enc):
    if Files.objects.filter(enc=enc).count() != 1:
        return HttpResponse("NO FILE")
    else:

        file = Files.objects.get(enc=enc)
        file.delete()
        return redirect('dolphine')


@login_required(login_url='/login/')
def download(request, enc):
    if Files.objects.filter(enc=enc).count() != 1:
        return HttpResponse("NO FILE")
    else:
        file = get_object_or_404(Files, enc=enc)
        file_path = file.file.path
        name = os.path.basename(file_path)
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(name)
        return response
