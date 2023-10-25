import json
import sys

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF

from admin_panel.models import Emails, TicketHd, Sms, SmsApi, UserAddOns, TicketTrans
from admin_panel.sms_hold import *
from meeting.models import MeetingHD

from reports.models import ReportForms, ReportLegend, LegendSubs, DepartmentReportMailQue
from servicing.models import Services, SubServices, ServiceCard, ServiceMaterials
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

        # write data
        if method == 'PUT':
            # save new service
            if module == 'services':
                service_code = data['service_code']
                service_description = data['service_description']
                service_name = data['service_name']
                service_owner = data['service_owner']

                Services(code=service_code, name=service_name, description=service_description,
                         owner_id=service_owner).save()

                t_service = Services.objects.get(code=service_code)

                # add sub
                SubServices(service=t_service, name=service_name, description=f"Default service for {service_name}",
                            owner_id=service_owner).save()

                success_response['message'] = "Serviced Added"

            # save job card
            elif module == 'jobcard':
                head = data.get('head')
                materials = data.get('materials')

                print(head)
                # get header data
                cardno = f"JC{ServiceCard.objects.all().count() + 1}"
                client_pk = head.get('client')
                client = User.objects.get(pk=client_pk)
                phone = head.get('phone').replace('+233', '0')
                owner = User.objects.get(pk=head.get('owner'))
                remarks = head.get('remarks')
                service = Services.objects.get(pk=head.get('service'))
                service_sub = SubServices.objects.get(pk=head.get('service_sub'))
                technician = User.objects.get(pk=head.get('technician'))
                importance = head.get('importance')
                tick = head.get('ticket')
                ticket_title = head.get('ticket_title')
                ticked_description = head.get('description')

                if tick == '0':
                    # generate
                    TicketHd(owner=client, title=f"{ticket_title}", descr=f"{ticked_description}", status=1).save()
                    ticket = TicketHd.objects.filter(owner=client, title=f"{ticket_title}", descr=f"{ticked_description}", status=1).last()
                else:
                    ticket2 = TicketHd.objects.get(pk=tick)
                    ticket2.status = 1
                    ticket2.title = ticket_title
                    ticket2.descr = ticket_title
                    ticket2.save()
                    ticket = TicketHd.objects.get(pk=tick)


                # save service card
                ServiceCard(client=client, owner=owner, remarks=f"{service.name}/{service_sub.name}/{ticket_title}", service=service, service_sub=service_sub,
                            technician=technician, ticket=ticket, importance=importance, cardno=cardno).save()

                just_service_card = ServiceCard.objects.all().last()

                # deal with materials
                for material in list(materials):
                    line = material['line']
                    item = material['item']
                    description = material['description']
                    price = material['price']
                    quantity = material['quantity']
                    total_price = material['total_price']

                    # save material
                    ServiceMaterials(line=line, item=item, description=description, price=price, quantity=quantity,
                                     total_price=total_price, service_card=just_service_card).save()

                # queue SMS
                Sms(api=SmsApi.objects.get(is_default=1),
                    message=f"A ticket has been opened for your query \n\nTICKET : "
                            f"{cardno} \n\nSERVICE "
                            f"TYPE : {service.name} \n\nTITLE : "
                            f"{ticket_title} \n\nYou can track service using the "
                            f"link below "
                            f"\n\nhttp://ocean.snedaghana.loc/servicing/jobcard/tracking/{just_service_card.cardno}/",
                    to=phone).save()

                success_response['message'] = "Job Opened"

            elif module == 'send_ticket_to_client':
                cardno = data.get('cardno')
                service = ServiceCard.objects.get(cardno=cardno)
                message = data.get('message')

                # get client details
                client = service.client
                client_details = UserAddOns.objects.get(user=client)

                sms = (
                    f"TICKET CLOSING\n\nTICKET No: {cardno}\n\nService Type: {service.service.name}\n\nMessage: {message}\n"
                    f"Final: use the link below to close or give further response to the ticket "
                    f"\n\nhttp://ocean.snedaghana.loc/servicing/jobcard/tracking/{cardno}/")

                print(DEFAULT_SMS_API)
                if SMS:
                    Sms(api_id=SMS_KEY, message=sms, to=client_details.phone).save()
                    service.client_approval = 1
                    service.save()
                    TicketTrans(ticket_id=service.ticket_id,
                                tran=f"Sent To {client.get_full_name()} for approval withm message {message}",
                                title="CLIENT APPROVAL", user_id=request.user.pk).save()
                    success_response['message'] = f"Sent To {client.get_full_name()} for approval and closing"
                else:
                    success_response['message'] = "Could Not Send SMS"




        # read data
        elif method == 'VIEW':
            if module == 'services':
                pk = data.get('pk') or '*'
                if pk == '*':
                    services = Services.objects.filter(status__gt=0)
                else:
                    servicing = Services.objects.filter(pk=pk, status__gt=0)

                if services.count() > 0:
                    arr = []
                    for servce in services:
                        subs = servce.subs()
                        ss = []
                        for sub in subs:
                            ss.append({
                                'pk': sub.pk,
                                'name': sub.name,
                                'desc': sub.description
                            })
                        arr.append({
                            'pk': servce.pk,
                            'code': servce.code,
                            'description': servce.description,
                            'subs': ss

                        })
                    success_response['message'] = arr
                else:
                    success_response['status_code'] = 404
                    success_response['message'] = f"NO SERVICES AVAILABLE {pk}"

            elif module == 'servicecard':
                cardno = data.get('cardno')

                if ServiceCard.objects.filter(cardno=cardno).exists():
                    card = ServiceCard.objects.get(cardno=cardno)
                    technician = User.objects.get(pk=card.technician_id)
                    cardpk = card.pk
                    print(cardpk)
                    materials = []
                    ticket_trans = []

                    for material in card.materials():
                        materials.append({
                            'line': material.line,
                            'item': material.item,
                            'description': material.description,
                            'price': material.price,
                            'quantity': material.quantity,
                            'total_price': material.total_price,

                        })

                    for ticktran in card.ticket.transactions():
                        ticket_trans.append({
                            'title': ticktran.title,
                            'descr': ticktran.tran,
                            'owner': {
                                'pk': ticktran.user.pk,
                                'username': ticktran.user.username,
                                'email': ticktran.user.email,
                                'fullname': f"{ticktran.user.first_name} {ticktran.user.last_name}",
                                'phone': UserAddOns.objects.get(user=ticktran.user).phone
                            },
                            'date': ticktran.created_on
                        })

                    header = {
                        'pk': card.pk,
                        'client': {
                            'pk': card.client.pk,
                            'username': card.client.username,
                            'email': card.client.email,
                            'fullname': f"{card.client.first_name} {card.client.last_name}",
                            'phone': UserAddOns.objects.get(user=card.client).phone
                        },
                        'owner': {
                            'pk': card.owner.pk,
                            'username': card.owner.username,
                            'email': card.owner.email,
                            'fullname': f"{card.owner.first_name} {card.owner.last_name}",
                            'phone': UserAddOns.objects.get(user=card.owner).phone
                        },
                        'remarks': card.remarks,
                        'service': {
                            'main': {
                                'code': card.service.code,
                                'name': card.service.name,
                                'description': card.service.description
                            },
                            'sub': {
                                'name': card.service_sub.name,
                                'description': card.service_sub.description
                            },
                        },
                        'technician': {
                            'pk': technician.pk,
                            'username': technician.username,
                            'email': technician.email,
                            'fullname': f"{technician.first_name} {technician.last_name}",
                            'phone': UserAddOns.objects.get(user=technician).phone
                        },
                        'ticket': {
                            'hd': {
                                'pk': card.ticket.pk,
                                'title': card.ticket.title,
                                'description': card.ticket.descr,
                                'status': card.ticket.status
                            },
                            'trans': ticket_trans
                        },
                        'importance': card.importance,
                        'status': card.status,
                        'timedata': {
                            'datecreated': card.created_date,
                            'timecreated': card.created_time,
                            'dateupdated': card.updated_date,
                            'timeupdated': card.updated_time
                        },
                        'materials': materials,
                        'next': {
                            'count': 0,
                            'code': 0
                        },
                        'prev': {
                            'count': 0,
                            'code': 0
                        }
                    }

                    if ServiceCard.objects.filter(id__gt=cardpk).exists():
                        header['next']['count'] = ServiceCard.objects.filter(id__gt=cardpk).count()
                        next_c = ServiceCard.objects.filter(id__gt=cardpk).first()
                        header['next']['nextcode'] = next_c.cardno

                    if ServiceCard.objects.filter(id__lt=cardpk).exists():
                        header['prev']['count'] = ServiceCard.objects.filter(id__lt=cardpk).count()
                        p_c = ServiceCard.objects.filter(id__lt=cardpk).last()

                        header['prev']['code'] = p_c.cardno

                    success_response['message'] = header

                else:
                    success_response['status_code'] = 404
                    success_response['message'] = "NO JOB CARD FOUND"



        # update data
        elif method == 'PATCH':
            if module == 'jobcardstatus':
                cardno = data.get('cardno')
                status = data.get('status')
                service = ServiceCard.objects.get(cardno=cardno)
                ticket = service.ticket
                owner = service.owner
                owner_details = UserAddOns.objects.get(user=owner)

                service.status = status
                service.save()
                Sms(to=owner_details.phone, message=f"Ticket has been closed\nTICKET NO: {cardno}",
                    api=SmsApi.objects.get(is_default=1)).save()
                mesg = "DOCUMENT UPDATED"
                if status == 0:
                    mesg = "DOCUMENT DELETED"
                    ticket.status = status
                    ticket.save()
                elif status == 2:
                    mesg = "DOCUMENT CLOSED"
                    # close ticket
                    ticket.status = status
                    ticket.save()

                success_response['message'] = mesg

            elif module == 'client_ticket_approval':
                cardno = data.get('cardno')
                service = ServiceCard.objects.get(cardno=cardno)
                ticket = service.ticket
                message = data.get('message')
                status = data.get('status')
                service.status = status
                if status == 2:
                    # approved
                    msg = f"TICKET: {cardno}\nSTATUS: Closed by Client\nMessage: {message}"
                    ticket.status = 2
                    ticket.save()

                else:
                    # not approved
                    service.status = 1
                    msg = f"TICKET: {cardno}\nSTATUS: Rejected by Client\nMessage: {message}"
                try:
                    Sms(api_id=SMS_KEY, message=msg, to='0546310011').save()
                    TicketTrans(title="Client Feedback", tran=msg, ticket_id=service.ticket_id,
                                user_id=request.user.pk).save()
                    success_response['message'] = "Feedback Sent"
                    service.client_approval = status
                    service.save()
                except Exception as e:
                    success_response['message'] = f"Feedback Not Sent {e}"

        # delete data
        elif method == 'DELETE':
            if module == 'services':
                service = data['service']
                serv = Services.objects.get(pk=service)
                name = serv.name
                serv.status = -1
                serv.save()

                success_response['message'] = f"{name} has been deleted"

            elif module == 'jobcard':
                cardno = data.get('cardno')
                service = ServiceCard.objects.get(cardno=cardno)
                owner = service.owner
                owner_details = UserAddOns.objects.get(user=owner)

                service.status = 0
                service.save()
                # Sms(to=owner_details.phone,message=f"Ticket has been closed\nTICKET NO: {cardno}",api=SmsApi.objects.get(is_default=1)).save()

                success_response['message'] = "Ticket Closed"



        # else
        else:
            success_response['status_code'] = 505
            success_response['message'] = f"Unknown  Request Method {method}"

        response = success_response


    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"

    return JsonResponse(response)
