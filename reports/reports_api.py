import json

from django.http import JsonResponse


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

    except Exception as e:
        response["status_code"] = 500
        response["message"] = f"{str(e)}"

    return JsonResponse(response)
