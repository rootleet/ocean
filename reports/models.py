from django.contrib.auth.models import User
from django.db import models

from admin_panel.models import Departments


class ReportLegend(models.Model):
    name = models.CharField(unique=True, null=False, blank=False, max_length=200)
    description = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=1)  # 1 active, 0 not, 99 done
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def subs(self):
        return LegendSubs.objects.filter(legend=self)


class LegendSubs(models.Model):
    name = models.CharField(unique=True, null=False, blank=False, max_length=200)
    action = models.CharField(unique=True, null=False, blank=False, max_length=200)
    description = models.TextField()

    legend = models.ForeignKey(ReportLegend, on_delete=models.SET_NULL, blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)



    # status = models.IntegerField(default=1)  # 1 active, 0 not, 99 done
    # owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)


class ReportForms(models.Model):
    key = models.CharField(unique=True, null=False, blank=False, max_length=200)
    description = models.TextField()
    code = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=1)  # 1 active, 0 not, 99 done
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)


class DepartmentReportMailQue(models.Model):
    department = models.ForeignKey(Departments,on_delete=models.CASCADE)
    files = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=0)

