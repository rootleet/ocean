import json

from django.http import JsonResponse

from meeting.models import MeetingHD


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
        doc = data.get('doc')
        key = data.get('key')
        output = data.get('output')
        header = {}
        transactions = []

        if doc == 'MET':
            head = MeetingHD.objects.filter(pk=key)




        success_response['message'] = {
            'header': header,
            'transactions': transactions
        }

        response = success_response


    except Exception as e:
        response["status_code"] = 500
        response["message"] = f"{str(e)}"

    return JsonResponse(response)
