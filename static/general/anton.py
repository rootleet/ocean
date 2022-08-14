# process completed with error
from django.http import HttpResponse


def err(message='An Error Occurred'):
    return HttpResponse(f'error%%{message}')


# process compiled no error
def done(message='Process Completed'):
    return HttpResponse(f'done%%{message}')
