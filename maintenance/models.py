from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class Maintenance(models.Model):
    title = models.CharField(max_length=226)
    description = models.TextField()

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_open = models.IntegerField(default=0) # 0 open, 1 in progress, 2 done
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)

    def status_html(self):
        obj = {
            'text': '',
            'color': ''
        }

        if self.is_open == 0:
            obj['text'] = 'reported'
            obj['color'] = 'bg-primary'
        elif self.is_open == 1:
            obj['text'] = 'in progress'
            obj['color'] = 'bg-info'
        elif self.is_open == 2:
            obj['text'] = 'closed'
            obj['color'] = 'bg-success'
        else:
            obj['text'] = 'unknown'
            obj['color'] = 'bg-dark'

        return obj

    def history(self):
        return MaintenanceHistory.objects.filter(maintenance=self).order_by('-pk')

class MaintenanceHistory(models.Model):
    title = models.CharField(max_length=226)
    description = models.TextField()
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
