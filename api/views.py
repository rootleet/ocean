from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from admin_panel.models import Notifications, AuthToken
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
    try:
        api_body = json.loads(request.body)
    except Exception as e:
        pass

    if module == 'notif':
        user = api_body['user']
        return get_notification(user=user)

    elif module == 'auth': # authentication model queried
        api_token = crud # api access token

        token_filter = AuthToken.objects.filter(token=api_token) # filter for token existence

        if token_filter.count() == 1: # if there is token
            token_d = AuthToken.objects.get(token=api_token)
            username = token_d.user.username
            password = token_d.user.password

            # login
            user = authenticate(request, username=username, password=password)

            try:
                # check if user is valid
                if hasattr(user, 'is_active'):
                    auth_login(request, user)
                    # Redirect to a success page.
                    return redirect('home')
                else:
                    messages.error(request,
                                   f"There is an error logging in, please check your credentials again or contact "
                                   f"Administrator")
                    return redirect('login')

            except Exception as e:
                messages.error(request, f"There was an error {e}")
                return redirect('login')

        else:
            return HttpResponse('INVALID TOKEN')


def index(request):
    return HttpResponse("NO OPRION")
