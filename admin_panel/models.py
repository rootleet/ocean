import pathlib

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from community.models import questions, QuestionTags
from blog.models import Providers
from django.db.models import Sum
from appconfig.models import *


# Create your models here.

class LoggedIssue(models.Model):
    issue = models.CharField(unique=True, max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def log_count(self):  # log count
        return LoggedIssue.objects.filter(issue=self.issue).count()

    def domain(self):  # tags
        # from community.models import QuestionTags
        quest = questions.objects.get(uni=self.issue)
        return quest.domain

    def owner(self):  # owner name
        owner_detail = questions.objects.get(uni=self.issue)
        owner_id = owner_detail.owner
        return User.objects.get(pk=owner_id)

    def title(self):
        return questions.objects.get(uni=self.issue).title

    def date_reported(self):
        return questions.objects.get(uni=self.issue).created_at

    def stat(self):
        if self.status == 0:
            return "PENDING"
        elif self.status == 1:
            return "TO SEND"
        else:
            return f"UNKNOWN ({self.status})"


class LoggedIssueTransaction(models.Model):
    issue = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(default=0)
    title = models.CharField(max_length=100)
    body = models.TextField()

    def owner(self):
        return User.objects.get(pk=self.created_by)


class PendingEscalations(models.Model):
    provider = models.CharField(max_length=5)
    issue = models.CharField(unique=True, max_length=100)

    def quest(self):
        return questions.objects.get(uni=self.issue)


class TaskHD(models.Model):  ## task model
    entry_uni = models.TextField()
    type = models.TextField()
    ref = models.TextField()
    owner = models.IntegerField(default=0)
    title = models.TextField()
    description = models.TextField()
    added_on = models.DateTimeField(auto_now=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    domain = models.ForeignKey('community.tags', on_delete=models.CASCADE)

    def url(self):
        return self.title.lower().replace(' ', '-')

    def owner_name(self):
        return User.objects.get(pk=self.owner).username

    def question(self):
        return questions.object.get(uni=self.ref)

    def provider(self):
        domain = self.domain.provider
        return domain


# task transactions
class TaskTrans(models.Model):
    entry_uni = models.TextField()
    tran_title = models.TextField()
    tran_descr = models.TextField()
    created_on = models.DateTimeField(auto_now=True)
    owner = models.IntegerField(default=0)

    def owner_name(self):
        return User.objects.get(pk=self.owner)


# email models
class Emails(models.Model):
    sent_from = models.TextField()
    sent_to = models.TextField()
    subject = models.TextField()
    body = models.TextField()
    email_type = models.TextField()
    ref = models.TextField()
    scheduled_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)
    status_message = models.TextField(default='Scheduled')
    sent_on = models.DateTimeField(auto_now=True)


class Sales(models.Model):
    loc = models.CharField(max_length=3)
    mech_no = models.TextField()
    gross_sales = models.DecimalField(max_digits=60, decimal_places=2)
    tax = models.DecimalField(max_digits=60, decimal_places=2)
    discount = models.DecimalField(max_digits=60, decimal_places=2)
    net_sales = models.DecimalField(max_digits=60, decimal_places=2)
    day = models.TextField()
    place = models.TextField()
    loc_desc = models.TextField()


class NotificationGroups(models.Model):
    full_name = models.TextField()
    email_addr = models.TextField()
    mobile_number = models.TextField()
    group = models.ForeignKey('EmailGroup', on_delete=models.CASCADE, default=0)


class EmailGroup(models.Model):
    group_name = models.TextField()
    def_domain = models.ForeignKey('community.tags', on_delete=models.CASCADE)
    description = models.TextField()
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def clients(self):
        return NotificationGroups.objects.filter(group=self.pk).count()


# tax modal
class TaxMaster(models.Model):
    tax_code = models.CharField(unique=True, max_length=2)
    tax_description = models.TextField()
    tax_rate = models.DecimalField(max_digits=3, decimal_places=2)
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)


class BankAccounts(models.Model):
    acct_name = models.CharField(unique=True, max_length=20)
    acct_serial = models.CharField(unique=True, max_length=12)
    acct_descr = models.TextField()
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)


class SuppMaster(models.Model):
    company = models.TextField()
    contact_person = models.TextField(default='NULL')
    purch_group = models.TextField()
    origin = models.TextField()
    email = models.TextField()
    mobile = models.TextField()
    city = models.TextField()
    street = models.TextField()
    taxable = models.IntegerField(default=1)
    bank_acct = models.ForeignKey('BankAccounts', on_delete=models.CASCADE)
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def location(self):
        return f"{self.origin} - {self.city}"


class ProductGroup(models.Model):
    descr = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def subgroups(self):
        return ProductGroupSub.objects.filter(group=self)


class ProductGroupSub(models.Model):
    group = models.ForeignKey('ProductGroup', on_delete=models.CASCADE)
    descr = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)


class ProductMaster(models.Model):
    group = models.ForeignKey('ProductGroup', on_delete=models.CASCADE)
    sub_group = models.ForeignKey('ProductGroupSub', on_delete=models.CASCADE)
    tax = models.ForeignKey('TaxMaster', on_delete=models.CASCADE)
    descr = models.TextField()
    shrt_descr = models.TextField()
    barcode = models.CharField(unique=True, max_length=255)
    supplier = models.ForeignKey('SuppMaster', on_delete=models.CASCADE)
    prod_img = models.FileField(upload_to=f'static/general/img/products/')

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def stock(self):
        if ProductTrans.objects.filter(product=self).aggregate(Sum('tran_qty'))['tran_qty__sum'] is None:
            return 0
        else:
            return ProductTrans.objects.filter(product=self).aggregate(Sum('tran_qty'))['tran_qty__sum']


class PackingMaster(models.Model):
    code = models.CharField(max_length=3, unique=True)
    descr = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)


class ProductPacking(models.Model):
    product = models.ForeignKey('ProductMaster', on_delete=models.CASCADE)
    packing_un = models.ForeignKey('PackingMaster', on_delete=models.CASCADE)
    pack_qty = models.DecimalField(max_digits=60, decimal_places=2)
    packing_type = models.CharField(default='U', max_length=1)

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def desc(self):
        return F"{self.pack_qty} IN 1{self.packing_un.descr}"


class ProductTrans(models.Model):
    loc = models.ForeignKey('Locations', on_delete=models.CASCADE)
    doc = models.CharField(max_length=2)
    doc_ref = models.TextField()
    product = models.ForeignKey('ProductMaster', on_delete=models.CASCADE)
    tran_qty = models.DecimalField(max_digits=65, decimal_places=2)

    def stock(self):
        if self.objects.filter(product=self.product.pk).aggregate(Sum('tran_qty'))['tran_qty__sum'] is None:
            return 0
        else:
            return self.objects.filter(product=self.product.pk).aggregate(Sum('tran_qty'))['tran_qty__sum']

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)


class AdjHd(models.Model):
    loc = models.ForeignKey('Locations', on_delete=models.CASCADE)
    remark = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def __set__(self, instance, value):
        return self.pk

    def trans(self):
        return AdjTran.objects.get(parent=self.pk)

    def tran_count(self):
        return AdjTran.objects.filter(parent=self.pk).count()

    def entry_no(self):
        return f"ADJ{self.pk}"


class AdjTran(models.Model):
    parent = models.ForeignKey('AdjHd', on_delete=models.CASCADE)
    line = models.IntegerField()
    product = models.ForeignKey('ProductMaster', on_delete=models.CASCADE)
    packing = models.TextField()
    quantity = models.DecimalField(max_digits=65, decimal_places=2)
    total = models.IntegerField()

    def product_name(self):
        return ProductMaster.objects.get(pk=self.product).descr


class Locations(models.Model):
    code = models.CharField(max_length=3, unique=True)
    descr = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)


class TransferHD(models.Model):
    loc_fr = models.ForeignKey('Locations', on_delete=models.CASCADE)

    loc_to = models.CharField(max_length=3)

    remark = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def to(self):
        return Locations.objects.get(pk=self.loc_to)

    def trans(self):
        return TransferTran.objects.get(parent=self.pk)

    def tran_count(self):
        return TransferTran.objects.filter(parent=self.pk).count()


class TransferTran(models.Model):
    parent = models.ForeignKey('TransferHD', on_delete=models.CASCADE)
    line = models.IntegerField()
    product = models.ForeignKey('ProductMaster', on_delete=models.CASCADE)
    packing = models.TextField()
    quantity = models.DecimalField(max_digits=65, decimal_places=2)
    total = models.IntegerField()

    def product_name(self):
        return ProductMaster.objects.get(pk=self.product).descr


class GrnHd(models.Model):
    loc = models.ForeignKey('Locations', on_delete=models.CASCADE)
    remark = models.TextField()
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def trans(self):
        return GrnTran.objects.get(parent=self.pk)

    def tran_count(self):
        return GrnTran.objects.filter(parent=self.pk).count()


class GrnTran(models.Model):
    parent = models.ForeignKey('TransferHD', on_delete=models.CASCADE)
    line = models.IntegerField()
    product = models.ForeignKey('ProductMaster', on_delete=models.CASCADE)
    packing = models.TextField()
    quantity = models.DecimalField(max_digits=65, decimal_places=2)
    total = models.IntegerField()

    def product_name(self):
        return ProductMaster.objects.get(pk=self.product).descr


class Notifications(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.IntegerField(default=0)  # 1 = success, 2 = information, 3 = warning, 4 = errpr
    title = models.TextField()
    descr = models.TextField()
    read = models.IntegerField(default=0)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)


class TicketHd(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.TextField()
    descr = models.TextField()

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)


class Files(models.Model):
    doc = models.CharField(max_length=3)
    cryp_key = models.CharField(max_length=60)
    media = models.FileField(upload_to=f'static/assets/uploads/%Y%m%d')

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    def file_name(self):
        return pathlib.PureWindowsPath(self.media.name).stem


class AuthToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)


# hold extra user details
class UserAddOns(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    about = models.TextField()
    company = models.TextField()
    position = models.TextField()
    country = models.TextField()
    Address = models.TextField()
    news = models.IntegerField(default=1)
    phone = models.CharField(max_length=14, unique=True)
    app_version = models.ForeignKey('appconfig.VersionHistory', on_delete=models.CASCADE)
    profile_pic = models.FileField(upload_to=f'static/general/img/users/')


class TaskBranchHD(models.Model):
    task = models.ForeignKey('TaskHD', on_delete=models.CASCADE)
    br_name = models.TextField()
    descr = models.TextField()
    md_hash = models.CharField(max_length=60, unique=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)

    def trans(self):
        return TaskBranchTran.objects.filter(parent=self.pk)


class TaskBranchTran(models.Model):
    parent = models.ForeignKey('TaskBranchHD', on_delete=models.CASCADE)
    descr = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


