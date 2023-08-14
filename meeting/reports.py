import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from meeting.models import MeetingHD


@csrf_exempt
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

        header = {}
        transactions = []

        if module == 'header':
            status = data.get('status')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            document = data.get('document')

            import openpyxl
            workbook = openpyxl.Workbook()
            sheet = workbook.active

            sheet['A1'] = 'TITLE'
            sheet['B1'] = 'START'
            sheet['C1'] = 'END'
            sheet['D1'] = 'OWNER'
            sheet['E1'] = 'STATUS'
            sheet['F1'] = "DATE CREATED"

            if status == '*':
                hd = MeetingHD.objects.filter(start_date__range=(start_date, end_date),
                                              end_date__range=(start_date, end_date))
            else:
                hd = MeetingHD.objects.filter(status=status, start_date__range=(start_date, end_date),
                                              end_date__range=(start_date, end_date))

            header['count'] = hd.count()
            sh_row = 2
            for meeting in hd:
                participants = meeting.participants()
                p_arr = []
                for participant in participants:
                    p_self = participant.myself()
                    p_obj = {
                        'name': p_self['name'],
                        'pk': p_self['pk']
                    }
                    p_arr.append(p_obj)

                # talking points
                points = meeting.talking_points()
                points_list = []
                for point in points:
                    points_list.append({
                        'pk': point.pk,
                        'point': point.title
                    })

                # files
                attachments = []
                meeting_attachments = meeting.attachments()
                for attachment in meeting_attachments:
                    attachments.append({
                        'path': attachment.media.url,
                        'name': attachment.file_name()
                    })

                if document == 'view':
                    obj = {
                        'pk': meeting.pk,
                        'uni': meeting.uni,
                        'title': meeting.title,
                        'descr': meeting.descr,
                        'start_end': {
                            'start_date': meeting.start_date,
                            'start_time': meeting.start_time,
                            'end_date': meeting.end_date,
                            'end_time': meeting.end_time
                        },
                        'created_date': meeting.created_date,
                        'created_time': meeting.created_time,
                        'status': meeting.status,
                        'participants': p_arr,
                        'points': points_list,
                        'attachments': attachments,
                        'owner': meeting.owner_details(),
                        'm_stat': meeting.m_stat()
                    }

                    transactions.append(obj)


                elif document == 'excel':
                    sheet[f'A{sh_row}'] = meeting.title
                    sheet[f'B{sh_row}'] = meeting.start_date
                    sheet[f'C{sh_row}'] = meeting.end_date
                    sheet[f'D{sh_row}'] = meeting.owner_details()['full_name']
                    sheet[f'E{sh_row}'] = meeting.m_stat()['text']
                    sheet[f'F{sh_row}'] = f"{meeting.created_date} {meeting.created_time}"

                    sh_row += 1

            if document == 'view':
                success_response['message'] = {
                    'header': header,
                    'transactions': transactions
                }

            elif document == 'excel':
                from datetime import datetime, date
                file_name = f"static/general/tmp/{start_date}_to_{end_date}_at_{date.today()}meeting.xlsx"
                workbook.save(file_name)
                success_response['message'] = file_name
        response = success_response


    except Exception as e:
        response["status_code"] = 500
        response["message"] = f"{str(e)}"

    return JsonResponse(response)
