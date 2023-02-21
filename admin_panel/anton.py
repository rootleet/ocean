from django.contrib.auth.models import User

from admin_panel.models import UserAddOns, UserSettings, Emails
#Sms, #SmsApi
from ocean import settings

#
# def push_notification(user_pk, subject='', message=''):
#     user = User.objects.get(pk=user_pk)
#     adon = UserAddOns.objects.get(user=user)
#     setting = UserSettings.objects.get(user=user)
#
#     if setting.prim_noif == 'email':
#         # send email
#         recipient_addr = user.email
#         Emails(sent_from=settings.EMAIL_HOST_USER, sent_to=recipient_addr, subject=subject,
#                body=message, email_type='system', ref='system').save()
#
#         pass
#     elif setting.prim_noif == 'mobile':
#         # send sms
#         sms_api = SmsApi.objects.get(sender_id='SNEDA SHOP')
#         Sms(api=sms_api, to=adon.phone, message=message).save()
#         # import requests
#         # import json
#         #
#         # url = "http://127.0.0.1:8000/sms/que/"
#         #
#         # payload = json.dumps({
#         #     "to": adon.phone,
#         #     "message": message
#         # })
#         # headers = {
#         #     'Content-Type': 'application/json',
#         #     'Cookie': 'csrftoken=LzknwT1ZM6hYeg0P8u5M9Wfyl7JWvOL2'
#         # }
#         #
#         # response = requests.request("GET", url, headers=headers, data=payload)
#         #
#         # print(response.text)
