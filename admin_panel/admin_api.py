import json
import sys

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib.auth.models import User, Permission
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.anton import md5only, remove_html_tags, generate_random_password
from admin_panel.cron_exe import execute_script
from admin_panel.models import DocApprovals, GeoCity, GeoCitySub, Reminder, SmsApi, UserAddOns, EvatCredentials, \
    Locations, \
    Departments, TicketTrans, Sms, TicketHd, MailSenders, MailQueues, MailAttachments
from blog.anton import make_md5
from reports.models import DepartmentReportMailQue
from servicing.models import ServiceCard
from taskmanager.models import Tasks, TaskTransactions


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

            elif module == 'set_loc_manager':
                mana_pk = data.get('manager')
                set_by_pk = data.get('mypk')
                loc_pk = data.get('loc_pk')

                manager = UserAddOns.objects.get(pk=mana_pk)
                set_by_pk = User.objects.get(pk=set_by_pk)
                location = Locations.objects.get(pk=loc_pk)

                location.manager = manager
                location.save()

                response= success_response

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
                                reminder.resp_message = f"{resp_msg} to {phone}"

                                reminder.status = 99
                                reminder.save()

                                sent += 1
                            else:
                                not_sent += 1
                        else:
                            # dont send
                            not_sent += 1

                        success_response['message'] = {
                            'sent': sent, 'pending': not_sent
                        }

                        response = success_response

            elif module == 'doc_app_auth':
                user_pk = data.get('user_pk')
                user = User.objects.get(pk=user_pk)
                doc_type = data.get('doc_type')
                DocApprovals(user=user, doc_type=doc_type).save()

                success_response['message'] = "Approver Added"
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

            elif module == 'evat_credentials':
                server_ip = data.get('server_ip')
                server_location = data.get('server_location')
                company_tin = data.get('company_tin')
                company_name = data.get('company_name')
                company_security_key = data.get('company_security_key')
                owner = data.get('owner')

                creating_user = User.objects.get(pk=owner)
                inv_req = f"http://{server_ip}/EvatAPI/api/EvatRequest"
                z_rez = f"http://{server_ip}/EvatAPI/api/EvatZreport"

                EvatCredentials(server_ip=server_ip, server_location=server_location, company_tin=company_tin,
                                company_name=company_name, company_security_key=company_security_key,
                                owner=creating_user, z_rez=z_rez, inv_req=inv_req).save()

                success_response['message'] = "Credential Saved"
                response = success_response

                pass

            elif module == 'location':
                print(data)
                server_ip = data.get('server_ip')
                server_location = data.get('server_location')
                code = data.get('code')
                descr = data.get('descr')
                db_user = data.get('db_user')
                db_password = data.get('db_password')
                db = data.get('db')
                owner = data.get('owner')
                creating_user = User.objects.get(pk=owner)
                Locations(server_location=server_location, ip_address=server_ip, code=code, descr=descr,
                          db_user=db_user, db=db, db_password=db_password, owner=creating_user).save()

                success_response = "LOCATION SAVED"
                response = success_response

            elif module == 'ticketupdate':
                date_time = data.get('datetime')
                ticket = data.get('ticket')
                title = data.get('title')
                description = data.get('description')
                owner = data.get('mypk')
                notify = data.get('notify')

                if ServiceCard.objects.filter(ticket_id=ticket).count() == 1:
                    service = ServiceCard.objects.get(ticket_id=ticket)
                    task = service.task
                    TaskTransactions(task=task, title=title, description=description, owner_id=owner).save()

                TicketTrans(ticket_id=ticket, title=title, tran=description, user_id=owner, created_on=date_time).save()

                if notify == 'YES':
                    tickethd = TicketHd.objects.get(pk=ticket)
                    tick_owner = tickethd.owner
                    user_details = UserAddOns.objects.get(user=tick_owner)
                    Sms(to=user_details.phone, message=f"TICKET UPDATE\nTitle: {title}\nDescription: {description}",
                        api=SmsApi.objects.get(is_default=1)).save()

                success_response['message'] = "TIcket Updated"
                response = success_response

            elif module == 'mail_senders':
                host = data.get('host')
                port = data.get('port')
                address = data.get('address')
                password = data.get('password')
                is_default = data.get('is_default')
                is_tls = data.get('is_tls')
                owner = User.objects.get(pk=data['mypk'])

                MailSenders(host=host, port=port, address=address, password=password, is_default=is_default,
                            is_tls=is_tls, owner=owner).save()
                success_response['message'] = "Sender Added"
                response = success_response

            elif module == 'que_mail':
                sender_pk = data.get('sender') or 'default'
                if sender_pk != 'default':
                    sender = MailSenders.objects.get(pk=data.get('sender'))
                else:
                    sender = MailSenders.objects.get(is_default=True)
                recipient = data.get('recipient')
                subject = data.get('subject')
                body = data.get('body')
                cc = data.get('cc')
                MailQueues(sender=sender, recipient=recipient, subject=subject, body=body, cc=cc).save()
                success_response['message'] = "Mail Added To Que"
                response = success_response

            elif module == 'broadcast_mail':
                sender = MailSenders.objects.get(is_default=True)
                users = UserAddOns.objects.all()
                message = data.get('body')
                subject = data.get('subject')
                for user in users:
                    us = user.user
                    email = us.email
                    body = message.replace('%name%', f"{us.get_full_name()}")
                    MailQueues(sender=sender, recipient=email, subject=subject, body=body, cc='').save()

                success_response['message'] = "Mail Added To Broadcast"
                response = success_response


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

            elif module == 'doc_app_auth':
                pin = data.get('pin')
                doc_type = data.get('doc_type')
                if UserAddOns.objects.filter(auth_pin=md5only(pin)).count() == 1:
                    # get user
                    us = UserAddOns.objects.get(auth_pin=md5only(pin))
                    # validate if user can auth
                    auth_user = us.user
                    if DocApprovals.objects.filter(user=auth_user, doc_type='sales_proforma').count() == 1:
                        success_response['status_code'] = 200
                        success_response['message'] = us.user.pk
                    else:
                        success_response['status_code'] = 505
                        success_response['message'] = "Permission Denied"
                else:
                    success_response['status_code'] = 404
                    success_response['message'] = f"Invalid User {md5only(1234)}"

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

            elif module == 'evat_credentials':
                keys = EvatCredentials.objects.all()
                arr = []
                for key in keys:
                    arr.append({
                        'pk': key.pk,
                        'server_ip': key.server_ip,
                        'server_location': key.server_location,
                        'company_tin': key.company_tin,
                        'company_name': key.company_name,
                        'company_security_key': key.company_security_key,
                        'inv_req': key.inv_req,
                        'z_rez': key.z_rez,
                        'status': key.stat()
                    })

                success_response['message'] = arr
                response = success_response

            elif module == 'dept_report':
                # get all department
                import openpyxl
                workbook = openpyxl.Workbook()

                departments = Departments.objects.all()
                from datetime import datetime
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
                day_only = current_datetime.strftime('%Y-%m-%d')

                for department in departments:
                    members = department.members()
                    head_email = department.email_of_head
                    files = []
                    for member in members:
                        sheet = workbook.active
                        sheet['A1'] = "TITLE"
                        #sheet['B1'] = "DESCRIPTION"
                        sheet['B1'] = "LAST TRANSACTION"
                        sheet['C1'] = "Transaction Time"
                        sheet['D1'] = "Status"
                        user = member.user

                        file_name1 = f"{user.first_name}_{user.last_name}_report_as_of_{formatted_datetime}.xlsx"

                        file_name = f"static/general/task-reports/{file_name1}"
                        # get tasks
                        user_tasks = Tasks.objects.filter(owner=member.user)
                        print(member.user.username, f"has {user_tasks.count()} tasks")
                        sheet_count = 2
                        updt = True
                        if user_tasks.count() > 0:
                            for task in user_tasks:
                                title = task.title
                                descr = remove_html_tags(task.description)
                                last_transaction_time = "NO TRANSACTION"
                                last_transaction = "NO TRANSACTION"

                                if task.transaction().count() > 0:
                                    transactions = task.transaction().last()
                                    if not transactions.reported:
                                        last_transaction = remove_html_tags(transactions.description)
                                        last_transaction_time = transactions.created_date
                                        transactions.reported = False
                                        updt = True

                                sheet[f"A{sheet_count}"] = title
                                # sheet[f'B{sheet_count}'] = descr
                                sheet[f'B{sheet_count}'] = last_transaction
                                sheet[f'C{sheet_count}'] = last_transaction_time
                                sheet[f"D{sheet_count}"] = task.text_status()

                                sheet_count += 1
                                # for transaction in transactions:
                                #     tran_title = transaction.title
                                #     tran_descr = transaction.description
                                #     date_time = f"{transaction.created_date} {transaction.created_time}"
                                #
                                #     sheet[f"A{sheet_count}"] = title
                                #     sheet[f"B{sheet_count}"] = tran_title
                                #     sheet[f"C{sheet_count}"] = tran_descr
                                #     sheet[f"D{sheet_count}"] = date_time
                                #     sheet[f"E{sheet_count}"] = "NOT KNOWN"
                                #
                                #     sheet_count += 1

                            workbook.save(file_name)
                            files.append(file_name)
                            if updt:
                                transactions.save()

                    if len(files) > 0:
                        print(department.name,"SENT")
                        MailQueues(
                            sender=MailSenders.objects.get(is_default=True),
                            recipient=department.email_of_head,
                            subject=f"{department.name} task report as of {day_only}",
                            body=f"Attached to this email is the departmental report for {department.name}"
                        ).save()

                        save_mail = MailQueues.objects.filter(
                            sender=MailSenders.objects.get(is_default=True),
                            recipient=department.email_of_head,
                            subject=f"{department.name} task report as of {day_only}",
                            body=f"Attached to this email is the departmental report for {department.name}",
                            is_sent=False
                        ).last()

                        for file in files:
                            print(file)
                            MailAttachments(mail=save_mail,attachment=file).save()
                        ##DepartmentReportMailQue(department=department, files=files).save()

                response = success_response
            elif module == 'auth':
                username = data.get('username')
                password = data.get('key')

                # check if user exist
                user = authenticate(request, username=username, password=password)

                try:
                    # check if user is valid
                    if hasattr(user, 'is_active'):
                        auth_login(request, user)
                        # Redirect to a success page.
                        msg = {
                            'auth': 'yes',
                            'pk': 1,
                            'username': username
                        }

                    else:
                        msg = {
                            'auth': 'no',
                            'error': "Check Credentials"
                        }

                except Exception as e:
                    msg = {
                        'auth': 'no',
                        'error': str(e)
                    }
                success_response['message'] = msg
                response = success_response
                print(response)

            elif module == 'users':
                all_users = User.objects.all()
                us = []
                for user in all_users:
                    obj = {
                        'pk': user.pk,
                        'username': user.username,
                        'fullname': f"{user.first_name} {user.last_name}"
                    }
                    us.append(obj)

                success_response['message'] = us
                response = success_response

            elif module == 'users_with_adon':
                all_users = UserAddOns.objects.all()
                us = []
                for usx in all_users:
                    obj = {
                        'pk': usx.pk,
                        'username': usx.user.username,
                        'fullname': f"{usx.user.first_name} {usx.user.last_name}",
                        'phone':usx.phone,
                        'email':usx.user.email,
                        'department':""
                    }
                    us.append(obj)

                success_response['message'] = us
                response = success_response

            elif module == 'cronjob':
                import datetime
                # Get the current time
                current_time = datetime.datetime.now().time()

                # Convert the current time to a string if needed
                current_time_str = current_time.strftime("%H:%M:%S")

                scripts = '/path/to/scripts/'
                # get jobs
                jobs = [
                    {
                        'name': 'hello-always',
                        'type': 'always',
                        'time': '00:00',
                        'exe': 'sync_html.sh'
                    },
                    {
                        'name': 'hello-sometime',
                        'type': 'timed',
                        'time': '12:00',
                        'exe': 'sync_emails.sh'
                    }
                ]

                # loop through Jobs
                for job in jobs:
                    j_name = job['name']
                    j_type = job['type']
                    j_time = job['time']
                    j_script = job['exe']
                    exe_script = f"{scripts}{j_script}"

                    if j_type == 'always' or (j_type == 'timed' and j_time >= current_time_str):
                        execute_script(exe_script)

            elif module == 'mail_senders':
                arr = []
                senders = MailSenders.objects.all()

                for sender in senders:
                    arr.append({
                        'host': sender.host,
                        'port': sender.port,
                        'address': sender.address,
                        'pk': sender.pk
                    })

                success_response['message'] = arr
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

            elif module == 'change_evat_engine':
                evat_key = data.get('evat_key')
                loc_key = data.get('loc_key')

                location = Locations.objects.get(pk=loc_key)
                evat_engine = EvatCredentials.objects.get(pk=evat_key)

                server_ip = location.ip_address
                db = location.db
                db_user = location.db_user
                db_pass = location.db_password

                company_name = evat_engine.company_name
                company_tin = evat_engine.company_tin
                company_security_key = evat_engine.company_security_key
                inv_req = evat_engine.inv_req
                z_rez = evat_engine.z_rez

                # connect to db
                import pyodbc

                # Create a connection string
                connection_str = (
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    f"SERVER={server_ip};"
                    f"DATABASE={db};"
                    f"UID={db_user};"
                    f"PWD={db_pass};"
                )
                # Create a connection
                connection = pyodbc.connect(connection_str)

                cursor = connection.cursor()
                cursor.execute(f"update sys_settings set sec_value = '{company_name}' where sec_key = 'COMPANY_NAMES'")

                cursor.execute(f"update sys_settings set sec_value = '{company_tin}' where sec_key = 'COMPANY_TIN'")

                cursor.execute(
                    f"update sys_settings set sec_value = '{company_security_key}' where sec_key = 'COMPANY_SECURITY_KEY'")

                cursor.execute(f"update sys_settings set sec_value = '{inv_req}' where sec_key = 'Evat_InvoiceReqApi'")

                cursor.execute(f"update sys_settings set sec_value = '{z_rez}' where sec_key = 'Evat_ZRepApi_url'")

                cursor.commit()
                cursor.close()

                connection.close()

                success_response['message'] = f"{location.descr} evat set to {evat_engine.server_location}"

                location.evat_key = evat_key
                location.save()

                response = success_response

            elif module == 'rest_password':
                pk = data.get('user')
                user = User.objects.get(pk=pk)
                addon = UserAddOns.objects.get(user=user)
                # generate new password
                new_password = generate_random_password()
                user.set_password(new_password)

                email_template = (
                    f"Dear {user.get_full_name()}, your password has been reset to <strong>{new_password}</strong>."
                    f" Logon to <a href='http://ocean.snedaghana.loc'>OCEAN</a> with credentials below<br>"
                    f"<strong>Username</strong> : {user.username}<br>"
                    f"<strong>Email</strong> : {user.email}<br>"
                    f"<strong>Password</strong> : {new_password}<br>")
                sms_message = (f"Your password for ocean has been reset, please logon using the crecentials below \n"
                               f"USERNAME: {user.username}\n"
                               f"Password:{new_password}")
                mail_api = MailSenders.objects.get(is_default=True)
                user.save()
                MailQueues(sender=mail_api, recipient=user.email, cc='solomon@snedaghana.com',
                           subject="PASSWORD RESET FOR OCEAN", body=email_template).save()
                Sms(api=SmsApi.objects.get(is_default=1), to=addon.phone, message=sms_message).save()

            elif module == 'all_password_reset':
                users = UserAddOns.objects.all()
                for user in users:
                    us = user.user
                    # generate new password
                    new_password = generate_random_password()
                    us.set_password(new_password)

                    email_template = (
                        f"Dear {us.get_full_name()}, your password has been reset to <strong>{new_password}</strong>."
                        f" Logon to <a href='http://ocean.snedaghana.loc'>OCEAN</a> with credentials below<br>"
                        f"<strong>Username</strong> : {us.username}<br>"
                        f"<strong>Email</strong> : {us.email}<br>"
                        f"<strong>Password</strong> : {new_password}<br>")
                    sms_message = (
                        f"Your password for ocean has been reset, please logon using the crecentials below \n"
                        f"USERNAME: {us.username}\n"
                        f"Password:{new_password}")
                    mail_api = MailSenders.objects.get(is_default=True)
                    us.save()
                    MailQueues(sender=mail_api, recipient=us.email, cc='solomon@snedaghana.com',
                               subject="PASSWORD RESET FOR OCEAN", body=email_template).save()
                    Sms(api=SmsApi.objects.get(is_default=1), to=user.phone, message=sms_message).save()

                success_response['message'] = "All Passwords Reset"
                response = success_response


        elif method == 'DELETE':  # delete

            if module == 'location':
                pk = data.get('pk')
                Locations.objects.get(pk=pk).delete()

                success_response['message'] = "LOCATION DELETED"
                response = success_response

        else:
            response['status_code'] = 503
            response['message'] = f"UKNOWN REQUEST METHOD ({method})"

    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno

        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"
        print(str(e))

    return JsonResponse(response)
