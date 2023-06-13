from datetime import datetime

from django.db import models

from inventory.models import Computer, ComputerGroup
from ocean import settings


# APPS GROUPS
class AppsGroup(models.Model):
    name = models.TextField()
    uni = models.CharField(max_length=60, unique=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)


class App(models.Model):
    group = models.ForeignKey('AppsGroup', on_delete=models.CASCADE)
    containers = models.ManyToManyField('AppContainer')
    name = models.TextField()
    uni = models.CharField(max_length=60, unique=True)
    description = models.TextField()
    icon = models.FileField(upload_to=f"static/files/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    root = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)
    version = models.IntegerField(default=0)


class VersionControl(models.Model):
    app = models.ForeignKey('App', on_delete=models.CASCADE)
    description = models.TextField()
    version_no = models.IntegerField()
    files = models.FileField(upload_to=f"static/uploads/appversion")

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)


class AppAssign(models.Model):
    app = models.ForeignKey('App', on_delete=models.CASCADE)
    mach = models.ForeignKey(Computer, on_delete=models.CASCADE)
    version = models.IntegerField(default=0)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now_add=True)
    updated_time = models.TimeField(auto_now_add=True)


class AppContainer(models.Model):
    name = models.CharField(max_length=255)
    computers = models.ManyToManyField(ComputerGroup)

    def __str__(self):
        return self.name
