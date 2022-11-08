from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from admin_panel.models import Notifications
import json

# Create your views here.
api_response = {
    'status': 505,
    'response': 'PROCEDURE ERROR'
}


def console(str=''):
    print()
    print(str)
    print()


def get_notification(user):
    if User.objects.filter(pk=user).count() == 1:
        notifications = Notifications.objects.filter(owner=User.objects.get(pk=user))
        if notifications.count() > 0:
            api_response['status'] = 200
            read = Notifications.objects.filter(owner=User.objects.get(pk=user), read=1)
            my_notif = [

            ]
            not_read = Notifications.objects.filter(owner=User.objects.get(pk=user), read=0)
            my_notifications = Notifications.objects.filter(owner=User.objects.get(pk=user)).order_by('-pk')[:5]

            for my_n in my_notifications:
                # 1 = success, 2 = information, 3 = warning, 4 = errpr
                icon = ''
                n_type = my_n.type
                if n_type == 1:
                    icon = 'bi-check-circle text-success'
                elif n_type == 2:
                    icon = 'bi-info-circle text-info'
                elif n_type == 3:
                    icon = 'bi-exclamation-circle text-warning'
                else:
                    icon = 'bi-exclamation-circle text-danger'
                    
                this_x = {
                    'title': my_n.title,
                    'type': my_n.type,
                    'descr': my_n.descr,
                    'status':my_n.read,
                    'icon':icon
                }
                my_notif.append(this_x)

            message = {
                'r_count': read.count(),
                'n_read': not_read.count(),
                'notifications': my_notif
            }
            api_response['response'] = message
        else:
            api_response['response'] = 'There is None'
        return JsonResponse(api_response, safe=False)
    else:
        return HttpResponse("USER NOT FOUND")


def api_call(request, module, crud):
    api_body = json.loads(request.body)
    if module == 'notif':
        user = api_body['user']
        return get_notification(user=user)


def index(request):
    return HttpResponse("NO OPRION")
