from django import forms

from meeting.models import *


class NewMeeting(forms.ModelForm):
    class Meta:
        model = MeetingHD
        exclude = ['created_date', 'created_time', 'status']


class NewMeetingTran(forms.ModelForm):
    class Meta:
        model = MeetingTrans
        exclude = ['created_date', 'created_time', 'status']


class NewMeetingTalkingPoint(forms.ModelForm):
    class Meta:
        model = MeetingTalkingPoints
        exclude = ['created_date', 'created_time', 'status']


class NewMeetingParticipant(forms.ModelForm):
    class Meta:
        model = MeetingParticipant
        exclude = ['created_date', 'created_time', 'status']
