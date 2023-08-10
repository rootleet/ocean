import json

from django.contrib import messages
from django.contrib.auth.models import User, Permission
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import GeoCity, GeoCitySub


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

        if method == 'PUT':  # write
            if module == 'geo':  # geographical condition
                part = data.get('part')

                if part == 'city' or part == 'region':  # add city
                    name = data.get('name')
                    us_pk = data.get('owner')

                    GeoCity(name=name, owner=User.objects.get(pk=us_pk)).save()
                    response = success_response
                elif part == 'sub':
                    city = data.get('city')
                    name = data.get('name')
                    us_pk = data.get('owner')

                    GeoCitySub(name=name, owner=User.objects.get(pk=us_pk), city=GeoCity.objects.get(pk=city)).save()
                    response = success_response

            elif module == 'tools':
                task = data.get('task')
                if task == 'set_message':
                    msg = data.get('message')
                    messages.success(request,msg)

            else:
                response['status_code'] = 503
                response['message'] = f"UNKNOWN MODULE ( METHOD : {method}, MODULE : {module} )"


        elif method == 'VIEW':  # read

            if module == 'geo':  # geographical condition
                part = data.get('part')

                if part == 'city' or part == 'region':  # add city
                    key = data.get('key')
                    cts = []
                    if key == '*':
                        cities = GeoCity.objects.all().order_by('name')
                    else:
                        from django.db.models import Q
                        cities = GeoCity.objects.filter(
                            Q(name__icontains=f"{key}") | Q(pk=f"{key}")).order_by('name')
                    for city in cities:
                        subj = []
                        for sub in city.subs():
                            subj.append({
                                'name': sub.name,
                                'pk': sub.pk
                            })
                        obj = {
                            'pk': city.pk,
                            'name': city.name,
                            'timestamp': city.timestamp(),
                            'subs': subj
                        }
                        cts.append(obj)

                    success_response['message'] = cts
                    response = success_response

            else:
                response['status_code'] = 503
                response['message'] = f"UNKNOWN MODULE ( METHOD : {method}, MODULE : {module} )"

        elif method == 'PATCH':  # update
            if module == 'user_permission':
                key = data.get('user')
                codename = data.get('codename')
                task = data.get('task')

                permission = Permission.objects.get(codename=codename)
                if User.objects.filter(pk=key).count() == 1:
                    user = User.objects.get(pk=key)
                    # Grant the permission to the user
                    if task == 'assign':
                        user.user_permissions.add(permission)
                        success_response['message'] = f"{codename} assigned to {user.username}"
                    elif task == 'remove':
                        user.user_permissions.remove(permission)
                        success_response['message'] = f"{codename} removed from {user.username}"
                    response = success_response

            pass

        elif method == 'DELETE':  # delete

            pass

        else:
            response['status_code'] = 503
            response['message'] = f"UKNOWN REQUEST METHOD ({method})"

    except Exception as e:
        response["status_code"] = 500
        response["message"] = f"{str(e)}"

    return JsonResponse(response)
