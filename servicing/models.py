from django.contrib.auth.models import User
from django.db import models

from admin_panel.models import TicketHd, UserAddOns, TicketTrans
from appscenter.models import App
from taskmanager.models import Tasks


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

    def jobs(self):
        return {
            'all': ServiceCard.objects.filter(service=self),
            'opened': ServiceCard.objects.filter(service=self, status=1),
            'closed': ServiceCard.objects.filter(service=self, status=2),
        }

    def technicians(self):
        return ServiceTechnicians.objects.filter(service=self)


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


class ServiceTechnicians(models.Model):
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    technician = models.ForeignKey(User, on_delete=models.CASCADE)

    def full_name(self):
        return f"{self.technician.get_full_name()}"

    class Meta:
        unique_together = (('service', 'technician'),)

    def phone(self):

        if UserAddOns.objects.filter(user=self.technician).exists():
            details = UserAddOns.objects.get(user=self.technician)
            return details.phone
        else:
            return 000


class ServiceCard(models.Model):
    cardno = models.CharField(max_length=10, unique=True, null=False, blank=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    remarks = models.TextField()
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    service_sub = models.ForeignKey(SubServices, on_delete=models.CASCADE)
    technician = models.ForeignKey(ServiceTechnicians, on_delete=models.CASCADE, related_name='technical')
    ticket = models.ForeignKey(TicketHd, on_delete=models.CASCADE)
    task = models.ForeignKey(Tasks, on_delete=models.SET_NULL, null=True, blank=False)
    app = models.ForeignKey(App, on_delete=models.SET_NULL, null=True, blank=False)
    importance = models.IntegerField(default=0)
    analysis = models.TextField(default='')

    status = models.IntegerField(default=1)  # 1 open, 2 closed, 0 deleted
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    client_approval = models.IntegerField(default=0)  # 0 not sent, 1 sent, 2 approved

    def materials(self):
        return ServiceMaterials.objects.filter(service_card=self)

    def materials_cost(self):
        filtered_sum = ServiceMaterials.objects.filter(service_card=self).aggregate(
            total_price_sum=models.Sum('total_price'))['total_price_sum'] or 0.00
        return 100

    def last_transaction(self):
        if TicketTrans.objects.filter(ticket_id=self.ticket_id).exists():
            tran = TicketTrans.objects.filter(ticket_id=self.ticket_id).last()
            return tran.tran
        else:
            return "No Transaction"

    def app_details(self):
        obj = {
            'name': 'none',
            'provider_email': 'none'
        }

        if App.objects.filter(pk=self.app.pk).exists():
            obj['name'] = self.app.name
            obj['provider_email'] = self.app.provider.email

        return obj

    def text_status(self):

        if self.client_approval == 0:
            return 'attending_to'

        if self.client_approval == 1:
            return 'sent_to_client'

        if self.client_approval == 2:
            return 'closed'

        if self.ticket.status == 0:
            return 'unattended'


class ServiceMaterials(models.Model):
    service_card = models.ForeignKey(ServiceCard, on_delete=models.CASCADE)
    line = models.IntegerField()
    item = models.TextField()
    description = models.TextField()
    price = models.DecimalField(max_digits=60, decimal_places=2)
    quantity = models.DecimalField(max_digits=60, decimal_places=2)
    total_price = models.DecimalField(max_digits=60, decimal_places=2)
