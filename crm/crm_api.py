import json
import sys

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from crm.models import Logs


@csrf_exempt
def api_interface(request):
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
            if module == 'log':
                description = data.get('description')
                flag = data.get('flag')
                name = data.get('name')
                phone = data.get('phone')
                subject = data.get('subject')
                mypk = data.get('mypk')

                Logs(description=description,flag=flag,customer=name,phone=phone,subject=subject,owner=User.objects.get(pk=mypk)).save()
                success_response['message'] = "Logged"
                response = success_response
        elif method == 'VIEW':
            if module == 'log':
                owner = data.get('owner')
                lg = Logs.objects.filter(owner=User.objects.get(pk=owner)).order_by('-pk')
                lgo = []
                for l in lg:
                    obj = {
                        'customer':l.customer,
                        'subject':l.subject,
                        'detail':l.description,
                        'date':l.created_date,
                        'time':l.created_time
                    }
                    lgo.append(obj)

                success_response['message'] = lgo
                response = success_response

    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response["message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"
        # response["message"] = f"Details: {e}"


    return JsonResponse(response)