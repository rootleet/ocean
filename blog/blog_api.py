import json
import sys

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.anton import make_md5_hash
from blog.models import articles


@csrf_exempt
def interface(request):
    response = {
        'status_code': 0,
        'message': ""
    }

    success_response = {
        'status_code': 200,
        'message': "Procedure Completed Successfully"
    }

    # get method
    method = request.method

    try:

        body = json.loads(request.body)
        module = body.get('module')
        data = body.get('data')

        if method == 'PUT':
            success_response['message'] = "Data Added"
            if module == 'new_article':
                owner = data.get('mypk')
                title = data.get('title')
                content = data.get('content')
                author = User.objects.get(pk=owner)
                tags = data.get('tags')
                uni = make_md5_hash(f"{title}{content}{tags}")

                # Save the object and get the pk
                new_article = articles(uni=uni, article=content, author=author, tag=tags, title=title)
                new_article.save()

                # Access the pk of the just-created object
                just_created_pk = new_article.pk
                success_response['message'] = uni


        else:
            success_response['status_code'] = 404
            success_response['message'] = "Unknown Method"
        response = success_response

    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"

    return JsonResponse(response)
