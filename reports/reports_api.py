import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF

from meeting.models import MeetingHD
from taskmanager.models import Tasks


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
        doc = data.get('doc')
        key = data.get('key')
        output = data.get('output')
        header = {}
        transactions = []

        if doc == 'TSK' and output == 'PDF':
            import re
            clean = re.compile('<.*?>')
            head = Tasks.objects.get(uni=key)
            pdf = FPDF('P', 'mm', 'A4')
            pdf.add_page()

            pdf.set_font('Arial', 'B', 16)
            pdf.cell(200, 5, head.title, 0, 1)
            pdf.ln(5)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, f"{re.sub(clean, '', head.description)}", 0, 'L')

            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(200, 5, 'TRANSACTIONS', 0, 1)
            pdf.ln(2)

            t_count = 1
            for tran in head.transaction():
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(200, 5, f'{t_count}. {tran.title}', 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.cell(200, 5, f"By {tran.owner.username} On {tran.created_date} {tran.created_time}", 0, 1)
                pdf.ln(1)
                pdf.multi_cell(0, 5, f"{re.sub(clean, '', tran.description)}", 0, 'L')
                pdf.ln(2)
                t_count += 1

            fil_name = f"static/general/tmp/test.pdf"
            pdf.output(fil_name, 'F')

            success_response['message'] = fil_name
            response = success_response




    except Exception as e:
        response["status_code"] = 500
        response["message"] = f"{str(e)}"

    return JsonResponse(response)
