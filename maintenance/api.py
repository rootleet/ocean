import json
import sys

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.anton import new_sms
from maintenance.models import Maintenance, MaintenanceHistory


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
            if module == 'maintenance_request':
                title = data.get('title')
                description = data.get('description')
                mypk = data.get('mypk')
                owner = User.objects.get(pk=mypk)

                maintenance = Maintenance(title=title, description=description, owner=owner)
                maintenance.save()
                sms_message = (f"NEW MAINTENANCE REQUEST\n\nTitle: {title}\n\nDescription: Sent Via Email or in "
                               f"ocean\n\nOwner: {owner.get_full_name()}")
                new_sms('0546310011',sms_message)
                success_response['message'] = "Service Logged"

            elif module == 'maintenance_log':
                maintenance = data.get('maintenance')
                mypk = data.get('mypk')
                title = data.get('title')
                description = data.get('description')

                # get objects
                main = Maintenance.objects.get(pk=maintenance)
                owner = User.objects.get(pk=mypk)

                # add to history
                history = MaintenanceHistory(maintenance=main,owner=owner,description=description,title=title)
                history.save()
                success_response['message'] = "Record Updated"

        elif method == 'PATCH':
            if module == 'close':
                maintenance = data.get('maintenance')
                mypk = data.get('mypk')
                message = data.get('message')
                main = Maintenance.objects.get(pk=maintenance)

                owner = User.objects.get(pk=mypk)
                history = MaintenanceHistory(title='CLOSING',description=message,owner=owner,maintenance=main)

                main.is_open = 2
                history.save()
                main.save()

                success_response['message'] = "Record Closed"


        response = success_response

    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"

    return JsonResponse(response, safe=False)