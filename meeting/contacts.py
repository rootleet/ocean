import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import Contacts


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
            # create
            full_name = data.get('full_name')
            email = data.get('email')
            phone = data.get('phone').replace('+233', '0')
            owner = data.get('owner')

            if Contacts.objects.filter(owner=User.objects.get(pk=owner), phone=phone):
                success_response['message'] = "You have a contact with same number"
            elif Contacts.objects.filter(owner=User.objects.get(pk=owner), email=email):
                success_response['message'] = "You have a contact with same email"
            else:
                Contacts(full_name=full_name, email=email, phone=phone, owner=User.objects.get(pk=owner)).save()
                success_response['message'] = "Contact Saved"
                # save

            response = success_response

        elif method == 'VIEW':
            owner = data.get('owner')
            key = data.get('key')
            me = User.objects.get(pk=owner)
            x_f = []
            if key == '*':
                contacts = Contacts.objects.filter(owner=me)
            else:
                contacts = Contacts.objects.filter(owner=me, pk=key)

            for contact in contacts:
                obj = {
                    'pk': contact.pk,
                    'name': contact.full_name,
                    'phone': contact.phone,
                    'email': contact.email
                }
                x_f.append(obj)

            success_response['message'] = x_f
            response = success_response


    except Exception as e:
        response["status_code"] = 500
        response["message"] = f"{str(e)}"

    return JsonResponse(response)
