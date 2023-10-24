

DEFAULT_SMS_API = {
    'status': False,
    'key': 0
}

from admin_panel.models import SmsApi  # Replace 'your_app' with the actual app name where SmsApi is defined
if SmsApi.objects.filter(is_default=1).count() == 1:
    DEFAULT_SMS_API['status'] = True
    DEFAULT_SMS_API['key'] = SmsApi.objects.get(is_default=1).pk

SMS = DEFAULT_SMS_API['status']
SMS_KEY = DEFAULT_SMS_API['key']