from django.contrib.auth.models import User
from django.db import models

from admin_panel.models import TicketHd


# services
class Services(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    status = models.IntegerField(default=1)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def subs(self):
        return SubServices.objects.filter(service=self)


class SubServices(models.Model):
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField()

    status = models.IntegerField(default=1)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class ServiceCard(models.Model):
    cardno = models.CharField(max_length=10, unique=True, null=False, blank=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    remarks = models.TextField()
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    service_sub = models.ForeignKey(SubServices, on_delete=models.CASCADE)
    technician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='technical')
    ticket = models.ForeignKey(TicketHd, on_delete=models.CASCADE)
    importance = models.IntegerField(default=0)

    status = models.IntegerField(default=1)  # 1 open, 2 closed, 0 deleted
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    client_approval = models.IntegerField(default=0)  # 0 not sent, 1 sent, 2 approved

    def materials(self):
        return ServiceMaterials.objects.filter(service_card=self)


class ServiceMaterials(models.Model):
    service_card = models.ForeignKey(ServiceCard, on_delete=models.CASCADE)
    line = models.IntegerField()
    item = models.TextField()
    description = models.TextField()
    price = models.DecimalField(max_digits=60, decimal_places=2)
    quantity = models.DecimalField(max_digits=60, decimal_places=2)
    total_price = models.DecimalField(max_digits=60, decimal_places=2)
