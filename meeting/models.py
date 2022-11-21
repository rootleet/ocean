from django.conf import settings
from django.db import models

from admin_panel.models import Files


# Create your models here.
class MeetingHD(models.Model):
    uni = models.CharField(max_length=60, unique=True)
    title = models.TextField()
    descr = models.TextField()

    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def m_stat(self):
        if self.status == 0:
            return {
                'class':f"btn btn-sm btn-danger",
                'text':"NOT STARTED"
            }
        elif self.status == 1:
            return {
                'class': f"btn btn-sm btn-info",
                'text': "ON GOING"
            }
        elif self.status == 3:
            return {
                'class': f"btn btn-sm btn-success",
                'text': "DONE"
            }
        else:
            return {
                'class': f"btn btn-sm btn-dark",
                'text': "UNKNOWN"
            }

    def attachments(self):
        return Files.objects.filter(doc='MET', cryp_key=self.uni)

    def participants(self):
        return MeetingParticipant.objects.filter(meeting=self.pk)

    def talking_points(self):
        return MeetingTalkingPoints.objects.filter(meeting=self.pk)


class MeetingTrans(models.Model):
    meeting = models.ForeignKey('MeetingHD', on_delete=models.CASCADE)
    talking_point = models.ForeignKey('MeetingTalkingPoints', on_delete=models.CASCADE)
    descr = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class MeetingTalkingPoints(models.Model):
    meeting = models.ForeignKey('MeetingHD', on_delete=models.CASCADE)
    title = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class MeetingParticipant(models.Model):
    meeting = models.ForeignKey('MeetingHD', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    present = models.IntegerField(default=0)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
