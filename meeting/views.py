import datetime
import hashlib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import Files, Emails
from admin_panel.views import page
from meeting.forms import NewMeeting, NewMeetingTalkingPoint
from meeting.models import MeetingHD, MeetingParticipant, MeetingTalkingPoints
from ocean import settings


# Create your views here.
@login_required()
def meeting(request):
    page['title'] = "Meetings"
    context = {
        'nav': True,
        'page': page,
        'meetings': MeetingHD.objects.all()[:20]
    }
    return render(request, 'meeting/index.html', context=context)


@login_required()
def open_meeting(request, meeting):
    page['title'] = "Meetings"
    meet = {
        'title': "Hello World",
        'descr': "Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui. Quisque velit nisi, pretium ut "
                 "lacinia in, elementum id enim. Vivamus magna justo, lacinia eget consectetur sed, convallis at "
                 "tellus. ",

    }
    context = {
        'nav': True,
        'page': page,
        'meeting': meet
    }
    return render(request, 'meeting/open.html', context=context)


@login_required(login_url='/login/')
def new_meeting(request):
    page['title'] = "New Meeting"
    md_mix = f"{datetime.datetime.now()} {request.user.last_login}{request.user.pk}{request.user.username}"
    hash_object = hashlib.md5(md_mix.encode())
    meeting_uni = hash_object.hexdigest()
    context = {
        'nav': True,
        'page': page,
        'm_uni': meeting_uni
    }
    return render(request, 'meeting/create.html', context=context)


@login_required(login_url='/login/')
def save_meeting(request):
    if request.method == 'POST':
        form = NewMeeting(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('config_meeting', form.cleaned_data['uni'])
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse(f"INVALID FORM {form}")
    else:
        return HttpResponse('INVALID REQUEST')
    return None


@login_required(login_url='/login/')
def meeting_config(request, meeting):
    meet = MeetingHD.objects.get(uni=meeting)
    page['title'] = f"MEETING / {meet.title}"
    context = {
        'nav': True,
        'page': page,
        'meeting': meet,
        'users': User.objects.all()
    }
    return render(request, 'meeting/live.html', context=context)


@login_required()
def add_participant(request):
    if request.method == 'POST':
        form = request.POST
        meeting_x = form['meeting']
        meet = MeetingHD.objects.get(pk=meeting_x)
        user_to_add = form.getlist('user_to_add')

        for us in user_to_add:
            user = User.objects.get(pk=us)
            if MeetingParticipant.objects.filter(user=us, meeting=meet).count() == 0:
                MeetingParticipant(meeting=meet, user=user).save()
                em_msg = f"You have been invited to a meeting <br><strong>Title</strong>: {meet.title} <br> " \
                         f"<strong>Time</strong>: {meet.start_date} {meet.start_time} to {meet.end_date} {meet.end_time} "

                Emails(sent_to=user.email, sent_from=settings.EMAIL_HOST_USER, subject="MEETING INVITATION",
                       body=em_msg, email_type='meeting_invitation', ref=meet.uni).save()
        return redirect('config_meeting', meet.uni)


def add_talking_point(request):
    if request.method == 'POST':
        form = NewMeetingTalkingPoint(request.POST)
        if form.is_valid():
            try:
                form.save()
                meeting = request.POST['meeting']
                meet = MeetingHD.objects.get(pk=meeting)
                return redirect('config_meeting', meet.uni)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse(form)


def remove_participant(request, meet, pk):
    participant = MeetingParticipant.objects.get(pk=pk)
    participant.delete()
    met = MeetingHD.objects.get(uni=meet)

    # check emails not sent
    not_sent_mails = Emails.objects.filter(ref=meet,email_type='meeting_invitation',status=0,sent_to=participant.user.email)
    if not_sent_mails.count() > 0:
        not_sent_mails.delete()
    else:
        em_msg = f"Your invitation a meeting has been canceled <br><strong>Title</strong>: {met.title} <br> " \
                             f"<strong>Time</strong>: {met.start_date} {met.start_time} to {met.end_date} {met.end_time} "
        Emails(sent_to=participant.user.email, sent_from=settings.EMAIL_HOST_USER, subject="MEETING CANCELLATION",
               body=em_msg, email_type='meeting_invitation', ref=meet).save()
    return redirect('config_meeting', meet)


def remove_point(request, meet, pk):
    tp = MeetingTalkingPoints.objects.get(pk=pk)
    tp.delete()
    return redirect('config_meeting', meet)

@csrf_exempt
def attach(request):
    if request.method == 'POST':
        form = request.POST
        cryp_key = form['cryp_key']
        doc = form['doc']
        media = request.FILES['media']


        Files(cryp_key=cryp_key, doc='MET', media=media).save()

        return HttpResponse('UPLOADED')


def end_meeting(request, meeting):
    met = MeetingHD.objects.get(uni=meeting)
    met.status = 3
    met.save()
    return redirect('open_meeting', meeting_config)