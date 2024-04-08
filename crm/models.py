import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


def get_username_on_delete(user):
    return user.username if user else None


class Sector(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def ob(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'owner': self.owner.get_full_name(),
            'is_active': self.is_active,
            'created_on': self.created_on
        }


class Positions(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def ob(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'owner': self.owner.get_full_name(),
            'is_active': self.is_active,
            'created_on': self.created_on
        }


# Create your models here.
class Logs(models.Model):
    customer = models.TextField(null=False, blank=False)
    success = models.BooleanField(default=True)
    phone = models.TextField()
    subject = models.TextField()
    description = models.TextField()
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=get_username_on_delete)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    company = models.TextField(blank=True)
    position = models.ForeignKey(Positions, on_delete=models.SET_NULL, null=True)
    email = models.TextField(blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)


class FollowUp(models.Model):
    log = models.ForeignKey(Logs, on_delete=models.CASCADE, null=False, blank=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='follow_up_user')
    follow_date = models.DateField(null=False, blank=False)

    is_open = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def daypass(self):
        if self.follow_date <= datetime.date.today():
            return True
        else:
            return False


class CrmUsers(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=get_username_on_delete)

    def last_logged(self):
        cts = self.logscount()
        if cts > 0:
            last_log = Logs.objects.filter(owner=self.user).last()
            return last_log.created_date
        else:
            return "NO"

    def logscount(self):
        return Logs.objects.filter(owner=self.user).count()


class Campaigns(models.Model):
    uni = models.CharField(unique=True, max_length=65)
    title = models.TextField()
    type = models.TextField()
    description = models.TextField()
    email_template = models.TextField()
    sms_template = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)


class CampaignTargets(models.Model):
    campaign = models.ForeignKey(Campaigns,on_delete=models.CASCADE)
    contact = models.CharField(max_length=65)
    name = models.TextField()

    class Meta:
        unique_together = (('campaign', 'contact'),)

