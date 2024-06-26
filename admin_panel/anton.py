import hashlib

from django.contrib.auth.models import User

from admin_panel.models import UserAddOns, UserSettings, Emails, Sms, SmsApi
from ocean import settings

import re


def is_valid_password(password):
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False

    # Check if password contains at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # Check if password contains at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False

    # Check if password contains at least one digit
    if not re.search(r'\d', password):
        return False

    # Check if password contains at least one special character
    if not re.search(r'[!@#$%^&*]', password):
        return False

    # If all checks pass, the password is considered valid
    return True


def push_notification(user_pk, subject='', message=''):
    user = User.objects.get(pk=user_pk)
    adon = UserAddOns.objects.get(user=user)
    setting = UserSettings.objects.get(user=user)

    if setting.prim_noif == 'email':
        # send email
        recipient_addr = user.email
        Emails(sent_from=settings.EMAIL_HOST_USER, sent_to=recipient_addr, subject=subject,
               body=message, email_type='system', ref='system').save()

        pass
    elif setting.prim_noif == 'mobile':
        # send sms
        sms_api = SmsApi.objects.get(sender_id='SNEDA SHOP')
        Sms(api=sms_api, to=adon.phone, message=message).save()
        # import requests
        # import json
        #
        # url = "http://127.0.0.1:8000/sms/que/"
        #
        # payload = json.dumps({
        #     "to": adon.phone,
        #     "message": message
        # })
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Cookie': 'csrftoken=LzknwT1ZM6hYeg0P8u5M9Wfyl7JWvOL2'
        # }
        #
        # response = requests.request("GET", url, headers=headers, data=payload)
        #
        # print(response.text)


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def make_md5_hash(text):
    from datetime import datetime
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
    new_text = f"{text}{formatted_datetime}"
    return hashlib.md5(new_text.encode('utf-8')).hexdigest()

def md5only(text):
    return hashlib.md5(str(text).encode('utf-8')).hexdigest()


def generate_random_password():
    import secrets
    import string
    characters = string.ascii_letters + string.digits  # Use letters and digits
    random_password = ''.join(secrets.choice(characters) for i in range(8))
    return random_password


def current_date():
    from datetime import datetime
    current_datetime = datetime.now()
    return current_datetime.strftime("%Y_%m_%d_%H_%M_%S")


def new_sms(to, message):
    api = SmsApi.objects.get(is_default=1)
    Sms(api=api, to=to, message=message).save()


def get_file_type(file_name):
    import os
    import mimetypes
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()  # Convert to lowercase for consistency

    # Use mimetypes to get the MIME type
    mime_type, _ = mimetypes.guess_type(file_name)

    return mime_type


def format_currency(amount):
    import locale

    # Set locale to the user's default setting (for example, 'en_US' for US)
    locale.setlocale(locale.LC_ALL, '')
    # Strip the currency symbol and return the formatted string
    try:
        return locale.currency(amount, grouping=True).strip(locale.localeconv()['currency_symbol']).strip()
    except Exception as e:
        return amount
