import os

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from admin_panel.anton import get_file_type

import admin_panel.models
from ocean import settings


# Create your models here.
class Maintenancex(models.Model):
    title = models.CharField(max_length=226)
    description = models.TextField()

    # owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_open = models.IntegerField(default=0)  # 0 open, 1 in progress, 2 done
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
    maintenance = models.ForeignKey(Maintenancex, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class MaintenanceAssetGroup(models.Model):
    name = models.CharField(max_length=60, unique=True, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def subgroups(self):
        return MaintenanceAssetSubGroup.objects.filter(group=self)

    def assets(self):
        return MaintenanceAsset.objects.filter(group=self)


class MaintenanceAssetSubGroup(models.Model):
    group = models.ForeignKey(MaintenanceAssetGroup, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=60, unique=True, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def assets(self):
        return MaintenanceAsset.objects.filter(subgroup=self)

    class Meta:
        unique_together = (('group', 'name'),)


class MaintenanceAsset(models.Model):
    sku = models.CharField(max_length=60, unique=True, null=False, blank=False)
    group = models.ForeignKey(MaintenanceAssetGroup, on_delete=models.CASCADE)
    subgroup = models.ForeignKey(MaintenanceAssetSubGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=60, unique=False, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='static/uploads/', null=False, blank=False)

    brand = models.CharField(max_length=200, default='Unknown')
    origin = models.CharField(max_length=200, default="Unknown")
    color = models.CharField(max_length=200, default="Unknown")
    location = models.ForeignKey(admin_panel.models.Locations, on_delete=models.SET_NULL, null=True)

    def image_link(self):
        return self.image.name


class Maintenance(models.Model):
    entry_no = models.CharField(max_length=10, unique=True, null=False, blank=False)
    asset = models.ForeignKey(MaintenanceAsset, on_delete=models.CASCADE)
    title = models.TextField(null=False)
    description = models.TextField(null=False)
    evidence = models.ImageField(upload_to='static/uploads/maintenance/attachments', null=False, blank=False)
    analyse = models.TextField(null=True)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='maintenance_v2')
    is_open = models.IntegerField(default=0)  # 0 open, 1 in progress, 2 done
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='technician')

    def transactions(self):
        return MaintenanceTransactions.objects.filter(maintenance=self)

    # def attachments(self):
    #     return MaintenanceAttachments.objects.filter(maintenance_id=self)

    # def materials(self):
    #     return MaintenanceMaterials.objects.filter(maintenance=self)

    def asset_obj(self):
        return {
            'sku': self.asset.sku,
            'group': self.asset.group.name,
            'subgroup': self.asset.subgroup.name,
            'name': self.asset.name,
            'image': self.asset.image_link(),
            'brand': self.asset.brand,
            'origin': self.asset.origin,
            'color': self.asset.color,
            'location':{
                'code':self.asset.location.code,
                'name':self.asset.location.descr
            }
        }

    def owner_obj(self):
        return {
            'username':self.owner.username,
            'name':self.owner.get_full_name()
        }
    
    def wo(self):
        obj = {
            'generated':False,
            'details':{}
        }
        if WorkOrder.objects.filter(w_request=self).count() == 1:
            obj['generated'] = True
            w_order = WorkOrder.objects.get(w_request=self)
            wo = {
                'wo_no':w_order.wo_no
            }
            obj['details'] = wo
        
        return obj
    
    # next entry
    def next_entry(self):
        val = 0

        if Maintenance.objects.filter(pk__gt=self.pk).count() > 0:
            rec = Maintenance.objects.filter(pk__gt=self.pk).first()
            val = rec.pk
        

        return val

    def previous_entry(self):
        val = 0

        if Maintenance.objects.filter(pk__lt=self.pk).count() > 0:
            rec = Maintenance.objects.filter(pk__lt=self.pk).last()
            val = rec.pk

        return val

    def get_evidence_url(self):
        return self.evidence.name or 'no-evidence'

class MaintenanceTransactions(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE)
    title = models.TextField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)


class WorkOrder(models.Model):
    wo_no = models.CharField(max_length=10,unique=True,null=False,blank=False)
    w_request = models.OneToOneField(Maintenance,on_delete=models.CASCADE,null=False,blank=False)
    technician = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='who_to_service')
    analyse = models.TextField(null=True)

    is_open = models.BooleanField(default=True)
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='who_generated')
    created_on = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    closed_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='who_closed')

    # additional class functions 
    def wr(self):
        obj = {
            'exist':False,
            'record':None
        }

        # check if job card exist
        if Maintenance.objects.filter(pk=self.w_request.pk).exists():
            obj['exist'] = True
            wri = Maintenance.objects.get(pk=self.w_request.pk)
            obj['record'] = {
                'pk':wri.pk,
                'entry_no':wri.entry_no,
                'title':wri.title,
                'description':wri.description,
                'evidence':wri.get_evidence_url(),
                'location':f"{wri.asset.location.code} - {wri.asset.location.descr}"
            }
            obj['asset'] = wri.asset_obj()

        return obj
    
    def metah(self):
        return {
            'date_created':self.created_on,
            'time_created':self.created_time,
            'created_by':self.owner.get_full_name()
        }

    def tech(self):
        return {
            'name':self.technician.get_full_name(),
            'username':self.technician.username,
            'pk':self.technician.pk
        }

    def materials(self):
        obj = {
            'available':False,
            'materials':[]
        }
        rec = []
        if WorkOrderMaterial.objects.filter(wo=self).exists():
            obj['available'] = True
            materials = WorkOrderMaterial.objects.filter(wo=self)
            for material in materials:
                rec.append({
                    'name':material.name,
                    'description':material.description,
                    'unit_price':material.unit_price,
                    'quantity':material.quantity,
                    'total':material.quantity * material.unit_price
                })
            obj['materials'] = rec
        
        return obj

    def attachments(self):
        obj = {
            'available':False,
            'attachments':[]
        }

        if WordOrderAttachments.objects.filter(wo=self).exists():
            obj['available'] = True
            attachments = WordOrderAttachments.objects.filter(wo=self)
            arr = []
            for attachment in attachments:
                arr.append({
                    'type':attachment.type,
                    'file':attachment.get_file_info(),
                    'owner':attachment.owner.get_full_name(),
                    'time': f"{attachment.date} {attachment.time}",
                    'description':attachment.description
                })
            obj['attachments'] = arr
        return obj

    # transactions
    def transactions(self):
        obj = {
            'available':False,
            'transactions':[]
        }
        arr = []

        if WordOrderTransactions.objects.filter(wo=self).exists():
            transactions = WordOrderTransactions.objects.filter(wo=self)
            obj['available'] = True
            for tran in transactions:
                arr.append({
                    'title':tran.title,
                    'description':tran.description,
                    'owner':tran.owner.get_full_name(),
                    'time':f"{tran.created_on} {tran.created_time}",
                    'evidence':tran.get_evidence_info(),
                    'date_time': tran.c_time()
                })
            obj['transactions'] = arr

        return obj

    # next entry
    def next_entry(self):
        val = 0

        if WorkOrder.objects.filter(pk__gt=self.pk).count() > 0:
            rec = WorkOrder.objects.filter(pk__gt=self.pk).first()
            val = rec.pk
        

        return val

    def previous_entry(self):
        val = 0

        if WorkOrder.objects.filter(pk__lt=self.pk).count() > 0:
            rec = WorkOrder.objects.filter(pk__lt=self.pk).last()
            val = rec.pk

        return val

# materials for a work order
class WorkOrderMaterial(models.Model):
    wo = models.ForeignKey(WorkOrder,on_delete=models.CASCADE)
    name = models.TextField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    unit_price = models.DecimalField(max_digits=60, null=False, blank=False,decimal_places=2)
    quantity = models.DecimalField(max_digits=60, null=False, blank=False,decimal_places=2)

    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)

# extra documents of a work order
class WordOrderAttachments(models.Model):
    wo = models.ForeignKey(WorkOrder,on_delete=models.CASCADE)
    type = models.TextField()
    description = models.TextField()
    file = models.FileField(upload_to='static/uploads/maintenance/attachments')

    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def get_file_info(self):
        file_info = {
            'url':'file-does-not-exist',
            'type':'unknwn/unknown',
            'name':'file-does-not-exist'
        }
        if self.file:
            file_exists = self.file.storage.exists(self.file.name)
            if file_exists:
                file_info = {
                    'url': self.file.url,
                    'type': get_file_type(self.file.name),
                    'name':os.path.splitext(self.file.name)[0].split('/')[-1]
                }
                

        return file_info


# updates on a work order as it happens
class WordOrderTransactions(models.Model):
    wo = models.ForeignKey(WorkOrder,on_delete=models.SET_NULL,null=True)
    title = models.TextField()
    description = models.TextField()
    evidence = models.FileField(upload_to='static/uploads/maintenance/attachments')

    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='who_logged_progeess')
    created_on = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_evidence_info(self):
        f_obj = {
                'exist':False
            }
        if self.evidence:
            
            file_exists = self.evidence.storage.exists(self.evidence.name)
            if file_exists:
                file_info = {
                    'url': self.evidence.url,
                    'type': get_file_type(self.evidence.name),
                    'name':os.path.splitext(self.evidence.name)[0].split('/')[-1]
                }
                f_obj['exist'] = True
                f_obj['file_info'] = file_info

        return f_obj

    def c_time(self):
        from datetime import datetime
        created_datetime = datetime.combine(self.created_on, self.created_time)
        return created_datetime.strftime("%Y-%m-%d %H:%M:%S")