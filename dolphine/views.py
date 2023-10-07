import hashlib
import os

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
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
        'files': Files.objects.filter(owner=request.user).order_by('-pk')
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


def rmbg(request):
    if request.method == 'POST' and request.FILES:
        uploaded_file = request.FILES['image']
        # Process the uploaded file here

        # Example: Get file details
        file_name = uploaded_file.name
        file_size = uploaded_file.size
        content_type = uploaded_file.content_type

        # Create a FileSystemStorage instance for static files
        fs = FileSystemStorage()

        # Generate a unique filename for the uploaded image
        file_name = fs.get_available_name(uploaded_file.name)

        # Save the uploaded file to a static directory
        file_path = os.path.join('static/rmbg/raw/', file_name)
        print(file_path)
        fs.save(file_path, uploaded_file)

        # remove bg
        import glob
        from rembg import remove
        from PIL import Image
        # Processing the image
        try:
            input = Image.open(file_path)
            file_name_with_extension = os.path.basename(file_path)
            out_file = f"static/rmbg/nobg/{file_name_with_extension}.png"
            # Removing the background from the given Image
            output = remove(input)

            # Saving the image in the given path
            output.save(out_file)
            print(f"SAVED: {out_file}")
            # move image to done
            # source_file_path = input_file
            # destination_folder_path = "static/rmbg/done/"
            # shutil.move(source_file_path, destination_folder_path)

            return JsonResponse({
                'success': True,
                'message': out_file
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e),
            })

