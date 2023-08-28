import json
import sys

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from taskmanager.models import Tasks

@csrf_exempt
def index(request):
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
            pass

        elif method == 'VIEW':
            if module == 'all':
                # get all meetings
                start_date = data.get('from')
                end_date = data.get('to')
                status = data.get('status')
                user = data.get('user')

                q_object = Q()
                if user:
                    q_object &= Q(owner=User.objects.get(pk=user))
                if start_date and end_date:
                    q_object &= Q(created_date__range=(start_date, end_date))
                if status:
                    if status != '*':
                        q_object &= Q(status=status)
                tasks = Tasks.objects.filter(q_object)

                tk =[]

                for task in tasks:
                    tk.append({
                        'title':task.title,
                        'uni':task.uni,
                        'description':task.description,
                        'task_inline':task.task_inline(),
                        'owner':task.owner.username,
                        'date':task.created_date
                    })

                success_response['message']=tk
                response = success_response


        elif method == 'PATCH':
            pass

        elif method == 'DELETE':
            pass

        else:
            success_response['message'] = "FORBIDDEN METHOD"
            success_response['status_code'] = 505
            response = success_response




    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response["message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"

    return JsonResponse(response)
