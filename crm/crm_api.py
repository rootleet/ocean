import json
import sys

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import Emails
from crm.models import Logs, CrmUsers


@csrf_exempt
def api_interface(request):
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
            if module == 'log':
                description = data.get('description')
                flag = data.get('flag')
                name = data.get('name')
                phone = data.get('phone')
                subject = data.get('subject')
                mypk = data.get('mypk')
                company = data.get('company')
                position = data.get('position')
                email = data.get('email')
                sector = data.get('sector')

                Logs(description=description, flag=flag, customer=name, phone=phone, subject=subject,
                     owner=User.objects.get(pk=mypk),
                     company=company, position=position, email=email, sector=sector).save()

                success_response['message'] = "Logged"
                response = success_response
            elif module == 'add_user':
                us_pk = data.get('user')
                us = User.objects.get(pk=us_pk)
                if CrmUsers.objects.filter(user=us).count() > 0:
                    pass
                else:
                    CrmUsers(user=us).save()

                success_response['message'] = f"{us.first_name} {us.last_name} ADDED"
                response = success_response

        elif method == 'VIEW':
            if module == 'log':
                owner = data.get('owner')
                lg = Logs.objects.filter(owner=User.objects.get(pk=owner)).order_by('-pk')
                lgo = []
                for l in lg:
                    obj = {
                        'customer': l.customer,
                        'subject': l.subject,
                        'detail': l.description,
                        'date': l.created_date,
                        'time': l.created_time,
                        'company': l.company,
                        'position': l.position,
                        'email': l.email,
                        'sector': l.sector,
                    }
                    lgo.append(obj)

                success_response['message'] = lgo
                response = success_response

            elif module == 'generate_log_report':
                from django.db.models import Count
                from django.db.models import Count, Q
                from datetime import date

                today = date.today()
                result = Logs.objects.filter(
                    Q(created_date=today)
                ).values('owner').annotate(owner_count=Count('owner'))
                import openpyxl
                attc = ''
                tr = ''
                result = CrmUsers.objects.all()
                for own in result:
                    workbook = openpyxl.Workbook()
                    owner = own.user
                    # start sheet
                    sheet = workbook.active
                    sheet['A1'] = "COMPANY"
                    sheet['B1'] = "CONTACT PERSON"
                    sheet['C1'] = "POSITION"
                    sheet['D1'] = "PHONE"
                    sheet['E1'] = "EMAIL"
                    sheet['F1'] = "FLAG"
                    sheet['G1'] = "DETAILS"
                    # get data
                    # user = User.objects.get(pk=owner)
                    us_logs = Logs.objects.filter(owner=owner, created_date=today)
                    l_count = us_logs.count()
                    tr += (f'<tr><td style="border: 1px solid black;">{owner.first_name} {owner.last_name}</td><td '
                           f'style="border: 1px solid black;">{l_count}</tr></tr>')
                    x_row = 2
                    for lg in us_logs:
                        comp_name = lg.company
                        contact_person = lg.customer
                        position = lg.position
                        phone = lg.phone
                        email = lg.email
                        flag = lg.flag
                        detail = lg.description

                        sheet[f'A{x_row}'] = comp_name
                        sheet[f'B{x_row}'] = contact_person
                        sheet[f'C{x_row}'] = position
                        sheet[f'D{x_row}'] = phone
                        sheet[f'E{x_row}'] = email
                        sheet[f'F{x_row}'] = flag
                        sheet[f'G{x_row}'] = detail

                        x_row += 1

                    from datetime import datetime
                    current_datetime = datetime.now()
                    formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
                    file_name1 = f"{owner.first_name}_{owner.last_name}_CRM_REPORT_{formatted_datetime}.xlsx"

                    file_name = f"static/general/crm-logs-reports/{file_name1}"
                    attc += f"{file_name1},"
                    workbook.save(file_name)
                    print(file_name)

                # add to emails
                body = f'<table><tr><th style="border: 1px solid black;">USER</th><th style="border: 1px solid ' \
                       f'black;">LOGS</th></td>{tr}</table>'
                Emails(sent_from='crm@snedaghana.com', sent_to='solomon@snedaghana.com',
                       subject=f"CRM REPORTS ON {today}",
                       body=body, email_type='crm', attachments=attc).save()

                success_response['message'] = "EMAILS LOG"
                response = success_response


    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {str(e)}"
        # response["message"] = f"Details: {e}"

    return JsonResponse(response, safe=False)
