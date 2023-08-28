from django.contrib.auth.models import User
from django.db import models

from ocean import settings


# Create your models here.
class Tasks(models.Model):
    title = models.TextField()
    uni = models.CharField(unique=True, null=False, max_length=255)
    description = models.TextField(null=False)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)  # 1 open, 2 close, 99 deleted
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def transaction(self):
        return TaskTransactions.objects.filter(task=self)

    def task_inline(self):
        if TaskTransactions.objects.filter(task=self).count() > 0:
            counts = TaskTransactions.objects.filter(task=self).count()
            last = TaskTransactions.objects.filter(task=self).last()
            return f"#{counts} updated on {last.created_date} by {last.owner.username}"
        else:
            return "no update"



class TaskTransactions(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.TextField()
    description = models.TextField(null=False)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)  # 1 active, 0 not, 99 done
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
