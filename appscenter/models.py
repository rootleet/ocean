from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from inventory.models import Computer, ComputerGroup
from ocean import settings


# app providers
class AppProviders(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


# APPS GROUPS
class AppsGroup(models.Model):
    name = models.TextField()
    uni = models.CharField(max_length=60, unique=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)


class App(models.Model):
    provider = models.ForeignKey(AppProviders, on_delete=models.CASCADE, default=1, blank=False, null=False)
    logo = models.ImageField(upload_to='static/uploads/apps/logos/', blank=True, null=True,default='static/apps/logos/default'
                                                                                           '.png')
    name = models.TextField()
    uni = models.CharField(max_length=60, unique=True)
    description = models.TextField()
    file = models.FileField(upload_to=f"static/uploads/apps/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    root = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)
    version = models.IntegerField(default=0)

    def latest_version(self):
        return VersionControl.objects.filter(app=self).order_by('-pk')[:1]

    def lastest_url(self):
        if VersionControl.objects.filter(app=self).exists():
            file = VersionControl.objects.filter(app=self).last()
            return file.files.url
        else:
            return '#'

    def prov(self):
        if self.provider == 'null':
            return False
        else:
            return True


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

    message = models.TextField(default='NULL')
    last_breath = models.TextField(default='NULL')


class AppContainer(models.Model):
    name = models.CharField(max_length=255)
    computers = models.ManyToManyField(ComputerGroup)

    def __str__(self):
        return self.name
