import json

import requests
from django.contrib import messages
from django.contrib.auth.models import User, Permission
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import GeoCity, GeoCitySub, Reminder, SmsApi, UserAddOns


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
                    messages.success(request, msg)

                elif task == 'check_reminders':
                    reminders = Reminder.objects.filter(status=1).order_by('rem_date', 'rem_time')
                    for reminder in reminders:
                        rem_time = reminder.rem_time
                        rem_date = reminder.rem_date
                        owner = reminder.owner

                        add_on = UserAddOns.objects.get(user=owner)

                        from datetime import datetime

                        # Assuming 'rem_time' is a time object and 'rem_date' is a date object
                        rem_datetime = datetime.combine(rem_date, rem_time)

                        # Get current date and time
                        current_datetime = datetime.now()
                        sent = 0
                        not_sent = 0
                        # Compare
                        if rem_datetime <= current_datetime:
                            # send
                            print(
                                f"The reminder {rem_datetime} datetime is less than or equal to the current datetime {current_datetime}")
                            sms_api = SmsApi.objects.get(is_default=1)
                            api_key = sms_api.api_key
                            sender = sms_api.sender_id
                            phone = add_on.phone
                            message = f"Title : {reminder.title} \nDate : {reminder.rem_date} \nTime : {reminder.rem_time} \nDetails : {reminder.message}"

                            endPoint = f"https://apps.mnotify.net/smsapi?key={api_key}&to={phone}&msg={message}&sender_id={sender}"
                            resp = requests.post(endPoint)
                            data = resp.json()

                            # status = data['status']
                            code = data['code']
                            resp_msg = data['message']

                            if code == '1000':
                                reminder.resp_code = code
                                reminder.resp_message = resp_msg

                                reminder.status = 0
                                reminder.save()

                                sent += 1
                            else:
                                not_sent +=1
                        else:
                            # dont send
                            not_sent += 1

                        success_response['message'] = {
                            'sent':sent,'pending':not_sent
                        }

                        response = success_response

            elif module == 'reminder':
                owner_pk = data.get('owner')
                title = data.get('title')
                message = data.get('message')
                date = data.get('date')
                time = data.get('time')

                Reminder(title=title, message=message, rem_date=date, rem_time=time,
                         owner=User.objects.get(pk=owner_pk)).save()
                success_response['message'] = "Reminder Scheduled"
                response = success_response

                # save reminder

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

            elif module == 'reminder':
                key = data.get('key')
                owner = data.get('owner')
                status = data.get('status')
                reminder_user = User.objects.get(pk=owner)

                if key == '*':
                    reminders = Reminder.objects.filter(owner=reminder_user).order_by('rem_date', 'rem_time')
                elif key == 'status':
                    reminders = Reminder.objects.filter(owner=reminder_user, status=status)
                else:
                    reminders = Reminder.objects.filter(owner=reminder_user, pk=key)

                rem = []

                for reminder in reminders:
                    obj = {
                        'pk': reminder.pk,
                        'title': reminder.title,
                        'message': reminder.message,
                        'date': reminder.rem_date,
                        'time': reminder.rem_time,
                        'status': reminder.status,
                        'owner': {
                            'pk': reminder.owner.pk,
                            'username': reminder.owner.username,
                            'name': f"{reminder.owner.first_name} {reminder.owner.last_name}"
                        }

                    }

                    rem.append(obj)

                success_response['message'] = rem
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

            elif module == 'reminder':
                date = data.get('date')
                time = data.get('time')
                title = data.get('title')
                message = data.get('message')
                key = data.get('pk')
                status = data.get('status')
                task = data.get('task')

                reminder = Reminder.objects.get(pk=key)
                if task == 'all':
                    reminder.rem_time = time
                    reminder.rem_date = date
                    reminder.title = title
                    reminder.message = message
                    success_response['message'] = "Reminder Updated"
                elif task == 'status':

                    if status == 'enable':
                        reminder.status = 1
                        success_response['message'] = "Reminder Disabled"
                    elif status == 'disable':
                        reminder.status = 0
                        success_response['message'] = "Reminder Enabled"
                    else:
                        success_response['message'] = f"Unknown status ({status}) set to reminder"

                reminder.save()
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
