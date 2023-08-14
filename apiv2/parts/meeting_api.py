import hashlib
import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import Contacts
from meeting.models import MeetingHD, MeetingParticipant, MeetingTalkingPoints


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

        if method == 'PUT':
            # create
            stage = data.get('stage')

            if stage == 'new_meeting':
                title = data.get('title')
                descr = data.get('descr')
                start_date = data.get('start_date')
                start_time = data.get('start_time')
                end_date = data.get('end_date')
                end_time = data.get('end_time')
                owner = data.get('owner')

                contacts = data.get('contacts')
                issues = data.get('issues')

                # Concatenate all string values
                str_to_hash = "{}{}{}{}{}{}{}".format(title, descr, start_date,
                                                      start_time, end_date, end_time, owner)
                # Create the hash object
                result = hashlib.md5(str_to_hash.encode())
                # Get the digest (hash value) in hexadecimal form
                uni = result.hexdigest()




                MeetingHD(uni=uni, title=title, descr=descr, start_date=start_date, start_time=start_time,
                          end_date=end_date, end_time=end_time, owner=User.objects.get(pk=owner)).save()

                meeting = MeetingHD.objects.get(uni=uni)
                try:
                    # add contacts
                    for contact in contacts:
                        cont = Contacts.objects.get(pk=contact)
                        phone = cont.phone
                        MeetingParticipant(meeting=meeting, name=cont).save()

                    # issues
                    for issue in issues:
                        if len(issue) > 0:
                            MeetingTalkingPoints(meeting=meeting, title=issue, owner=User.objects.get(pk=owner)).save()

                    success_response['message'] = uni

                    response = success_response
                except Exception as e:
                    meeting.delete()
                    response['status_code'] = 505
                    response['message'] = f"Meeting could not be saved {e}"

        elif method == 'VIEW':

            if module == 'meetings':
                part = data.get('part')
                key = data.get('key')
                meet = []
                if part == 'mine':
                    meetings = MeetingHD.objects.filter(owner=User.objects.get(pk=key))

                elif part == 'live' or part == 'single':
                    meetings = MeetingHD.objects.filter(pk=key)

                for meeting in meetings:
                    # load participant
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
                        'attachments':attachments
                    }
                    meet.append(obj)

            success_response['message'] = meet
            response = success_response

        elif method == 'PATCH':
            if module == 'start_meeting':
                uni = data.get('uni')
                meeting = MeetingHD.objects.get(uni=uni)
                meeting.status = 1
                meeting.save()

                success_response['message'] = uni
                response = success_response

            elif module == 'end_meeting':
                uni = data.get('uni')
                document = data.get('document')
                meeting = MeetingHD.objects.get(uni=uni)

                print(document)

                meeting.status = 3
                meeting.document = document
                meeting.save()

                success_response['message'] = uni
                response = success_response

    except Exception as e:
        response["status_code"] = 500
        response["message"] = f"{str(e)}"

    return JsonResponse(response)
