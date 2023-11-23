import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from appscenter.models import AppProviders


@csrf_exempt
def interface(request):
    method = request.method
    response = {"status_code": "", "status": "", "message": ""}

    try:
        body = json.loads(request.body)
        module = body.get('module')
        data = body.get('data')

    except json.JSONDecodeError as e:
        response["status_code"] = 400
        response["status"] = "Bad Request"
        response["message"] = f"Error decoding JSON: {e.msg}"
        return JsonResponse(response)

    try:
        response['status_code'] = 200
        if method == "PUT":
            response['message'] = "Record Saved"
            if module == 'provider':
                name = data.get('name')
                email = data.get('email')
                phone = data.get('phone')
                description = data.get('description')
                country = data.get('country')
                city = data.get('city')
                owner = User.objects.get(pk=data.get('mypk'))
                AppProviders(name=name, email=email, phone=phone, description=description, country=country, city=city, owner=owner).save()

            elif method == 'VIEW':
                if module == 'provider':
                    providers = AppProviders.objects.all()
                    ps = []
                    for provider in providers:
                        ps.append({
                            "name": provider.name,
                            "email": provider.email,
                            "phone": provider.phone,
                            "description": provider.description,
                            "country": provider.country,
                            "city": provider.city,
                            "pk":provider.pk
                        })
                    response['message'] = ps

    except Exception as e:
        import traceback

        response["status_code"] = 400
        response["status"] = "Error"
        response["message"] = f"{e} {traceback.print_exc(limit=1)} - {traceback.format_exc()}"

    return JsonResponse(response)