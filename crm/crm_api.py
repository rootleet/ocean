import json
import sys

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from admin_panel.anton import make_md5_hash
from admin_panel.models import Emails, MailQueues, MailSenders, MailAttachments, Reminder
from crm.models import Logs, CrmUsers, Sector, Positions, FollowUp


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
                description = data.get('details')
                flag = data.get('flag')
                if flag == 'success':
                    flag = True
                else:
                    flag = False
                name = data.get('contact_person')
                phone = data.get('phone')
                subject = data.get('subject')
                mypk = data.get('mypk')
                company = data.get('company_name')
                position = data.get('position')
                email = data.get('email')
                sector = data.get('sector')

                print(data)
                current_datetime = timezone.now()
                formatted_date = current_datetime.strftime('%Y-%m-%d')
                created_date = data.get('date', formatted_date)

                Logs(description=description, success=flag, customer=name, phone=phone, subject=subject,
                     owner=User.objects.get(pk=mypk),
                     company=company, position_id=position, email=email, sector_id=sector,
                     created_date=created_date).save()
                saved_log = Logs.objects.filter(
                    description=description, success=flag, customer=name, phone=phone, subject=subject,
                    owner=User.objects.get(pk=mypk),
                    company=company, position_id=position, email=email, sector_id=sector,
                    created_date=created_date
                ).last().pk

                success_response['message'] = saved_log
                response = success_response

            elif module == 'follow_up':
                print(data)
                log = data.get('log')
                mypk = data.get('mypk')
                follow_date = data.get('follow_date')

                lg = Logs.objects.get(pk=log)
                owner = User.objects.get(pk=mypk)

                FollowUp(log=lg, owner=owner, follow_date=follow_date).save()

                # add reminder
                Reminder(title="Customer Follow Up", message=f"Follow up with {lg.customer} about {lg.subject}",
                         rem_date=follow_date, rem_time="08:30:00", owner=owner, read_only=True).save()

                success_response['message'] = "Follow Up Added"
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
            elif module == 'sector':
                sector = data.get('sector')
                own_pk = data.get('mypk')
                owner = User.objects.get(pk=own_pk)
                Sector(owner=owner, name=sector).save()
                success_response['message'] = "Sector added"

            elif module == 'position':
                sector = data.get('position')
                own_pk = data.get('mypk')
                owner = User.objects.get(pk=own_pk)
                Positions(owner=owner, name=sector).save()
                success_response['message'] = "Position added"

        elif method == 'VIEW':
            if module == 'log':
                from django.db.models import Q
                from datetime import datetime

                doc = data.get('doc', 'JSON')
                # Define your filters
                owner_filter = data.get('owner',
                                        '*')  # Replace "owner_name" with the actual owner name you want to filter on
                flag_filter = data.get('flag')
                flag = False
                if flag_filter == 'success':
                    flag = True
                start_date = data.get('start_date', None)  # Replace with your start date
                end_date = data.get('end_date', None)  # Replace with your end date
                position_filter = data.get('position')  # Replace None with the actual position you want to filter on
                sector_filter = data.get('sector')  # Replace None with the actual sector you want to filter on

                queryset = Logs.objects.all()
                if owner_filter != '*':
                    queryset = queryset.filter(owner__id=owner_filter)

                if flag_filter is not None and flag_filter != '*':
                    queryset = queryset.filter(flag=flag)

                if start_date is not None and end_date is not None:
                    queryset = queryset.filter(created_date__range=(start_date, end_date))

                if position_filter is not None and position_filter != '*':
                    queryset = queryset.filter(position_id=position_filter)

                if sector_filter is not None and position_filter != '*':
                    queryset = queryset.filter(sector_id=sector_filter)

                lgo = []
                if doc == 'JSON':
                    for l in queryset:
                        obj = {
                            'customer': l.customer,
                            'subject': l.subject,
                            'detail': l.description,
                            'date': l.created_date,
                            'time': l.created_time,
                            'company': l.company,
                            'position': l.position.name,
                            'email': l.email,
                            'sector': l.sector.name,
                            'success': l.success,
                            'phone': l.phone
                        }

                        lgo.append(obj)
                elif doc == 'excel':
                    import openpyxl
                    book = openpyxl.Workbook()
                    sheet = book.active
                    sheet.title = "CRM Report"

                    sheet["A1"] = "Company"
                    sheet["B1"] = "Sector"
                    sheet['C1'] = "Contact Person"
                    sheet['D1'] = "Position"
                    sheet['E1'] = "Entry Date"
                    sheet['F1'] = "Phone"
                    sheet['G1'] = 'Email'
                    sheet['H1'] = "Subject"
                    sheet['I1'] = "Statue"
                    sheet['J1'] = "Response"

                    sheet_row = 2
                    for log in queryset:
                        sheet[f"A{sheet_row}"] = log.company
                        sheet[f"B{sheet_row}"] = log.sector.name
                        sheet[f"C{sheet_row}"] = log.customer
                        sheet[f"D{sheet_row}"] = log.position.name
                        sheet[f"E{sheet_row}"] = log.created_date
                        sheet[f"F{sheet_row}"] = log.phone
                        sheet[f"G{sheet_row}"] = log.email
                        sheet[f"H{sheet_row}"] = log.subject
                        sheet[f"I{sheet_row}"] = log.success
                        sheet[f"J{sheet_row}"] = log.description
                        sheet_row += 1

                    # save file
                    nn = make_md5_hash(datetime.now())
                    file_name = f'static/general/tmp/crm_report_{nn}.xlsx'
                    book.save(file_name)
                    lgo = file_name

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
                    # get data
                    # user = User.objects.get(pk=owner)
                    owner = own.user
                    us_logs = Logs.objects.filter(owner=owner, created_date=today)
                    l_count = us_logs.count()

                    tr += (f'<tr><td style="border: 1px solid black;">{owner.first_name} {owner.last_name}</td><td '
                           f'style="border: 1px solid black;">{l_count}</tr></tr>')
                    if l_count > 0:
                        # make attachment
                        workbook = openpyxl.Workbook()

                        # start sheet
                        sheet = workbook.active
                        sheet['A1'] = "COMPANY"
                        sheet['B1'] = "CONTACT PERSON"
                        sheet['C1'] = "POSITION"
                        sheet['D1'] = "PHONE"
                        sheet['E1'] = "EMAIL"
                        sheet['F1'] = "Success"
                        sheet['G1'] = "DETAILS"

                        x_row = 2
                        for lg in us_logs:
                            print(lg)
                            comp_name = lg.company
                            contact_person = lg.customer
                            position = lg.position.name
                            phone = lg.phone
                            email = lg.email
                            flag = lg.success
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

                        file_name = f"static/attachments/{file_name1}"
                        attc += f"{file_name},"
                        workbook.save(file_name)
                        print(file_name)

                # add to emails
                body = f'<table><tr><th style="border: 1px solid black;">USER</th><th style="border: 1px solid ' \
                       f'black;">LOGS</th></td>{tr}</table>'
                print(tr)
                cc = "uyinsolomon2@gmail.com,solomon@snedaghana.com"
                # Emails(sent_from='crm@snedaghana.com', sent_to='bharat@snedaghana.com',
                #        subject=f"CRM REPORTS ON {today}",
                #        body=body, email_type='crm', attachments=attc, cc=cc).save()
                #
                # Emails(sent_from='crm@snedaghana.com', sent_to='solomon@snedaghana.com',
                #        subject=f"CRM REPORTS ON {today}",
                #        body=body, email_type='crm', attachments=attc, cc=cc).save()

                MailQueues(
                    sender=MailSenders.objects.get(is_default=1),
                    recipient='solomon@snedaghana.com',
                    body=body,
                    subject=f"CRM REPORTS ON {today}",
                    cc=cc
                ).save()
                mail = MailQueues.objects.all().last()
                for attchment in attc.split(','):
                    if len(attchment) > 0:
                        MailAttachments(mail=mail, attachment=attchment).save()

                success_response['message'] = "EMAILS LOG"
                response = success_response

            elif module == 'sector':
                key = data.get('key', '*')
                arr = []
                if key == '*':
                    sectors = Sector.objects.all().order_by('name')
                else:
                    sectors = Sector.objects.get(pk=key)

                for sector in sectors:
                    arr.append(sector.ob())

                success_response['message'] = arr

                response = success_response

            elif module == 'position':
                key = data.get('key', '*')
                arr = []
                if key == '*':
                    positions = Positions.objects.all().order_by('name')
                else:
                    positions = Positions.objects.get(pk=key)

                for position in positions:
                    arr.append(position.ob())

                success_response['message'] = arr

                response = success_response


            else:
                response = {'message': 'NO MODULE FOUND', 'status_code': 404}

    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {str(e)}"
        # response["message"] = f"Details: {e}"
        print(e)

    return JsonResponse(response, safe=False)
