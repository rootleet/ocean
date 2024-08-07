import os.path
import pathlib

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from community.models import questions, QuestionTags
from blog.models import Providers
from django.db.models import Sum
from appconfig.models import *
from datetime import datetime




# Create your models here.

def format_currency(amount):
    import locale

    # Set locale to the user's default setting (for example, 'en_US' for US)
    locale.setlocale(locale.LC_ALL, '')
    # Strip the currency symbol and return the formatted string
    try:
        return locale.currency(amount, grouping=True).strip(locale.localeconv()['currency_symbol']).strip()
    except Exception as e:
        return amount

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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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

    entry_date = models.DateField()
    support_by = models.TextField(default='not set')

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
    cc = models.TextField(blank=True)
    scheduled_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)
    status_message = models.TextField(default='Scheduled')
    sent_on = models.DateTimeField(auto_now=True)
    attachments = models.TextField(blank=True)

    def send_cc(self):
        cc = self.cc.rstrip(',')
        return cc.split(',')


class MailSenders(models.Model):
    host = models.TextField()
    port = models.TextField()
    address = models.CharField(max_length=200, unique=True)
    password = models.TextField()
    is_default = models.BooleanField(default=False)
    is_tls = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=200,null=True,blank=True)

    def mail_counts(self):
        return {
            'sent': MailQueues.objects.filter(sender=self, is_sent=True).count(),
            'not_sent': MailQueues.objects.filter(sender=self, is_sent=False).count()
        }

    def mails(self):
        MailQueues.objects.filter(sender=self)


class MailGroup(models.Model):
    name = models.CharField(max_length=66, unique=True, null=False, blank=False)


class MailQueues(models.Model):
    group = models.ForeignKey(MailGroup, on_delete=models.SET_NULL, default=None, null=True)
    sender = models.ForeignKey(MailSenders, on_delete=models.CASCADE)
    recipient = models.EmailField()
    subject = models.TextField()
    body = models.TextField()
    cc = models.TextField(blank=True)
    scheduled_on = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    sent_on = models.DateTimeField(auto_now=True)
    sent_response = models.TextField(blank=True, default="NOT SENT")

    def has_attachments(self):
        return MailAttachments.objects.filter(mail=self).count()

    def attachments(self):
        return MailAttachments.objects.filter(mail=self)

    def copied(self):
        return len(self.cc.split(','))


class MailAttachments(models.Model):
    mail = models.ForeignKey(MailQueues, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='static/attachments/')


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
    tax_rate = models.DecimalField(max_digits=10, decimal_places=2)

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
    prod_img = models.FileField(upload_to=f'static/uploads/products/')

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    # price_center = models.ForeignKey('inventory.PriceCenter', on_delete=models.CASCADE)

    def obj(self):
        return {
            "barcode":self.barcode,
            "name":self.descr,
            "group":self.group.descr,
            "supplier":self.supplier.company,
            "sub_group":self.sub_group.descr
        }
    def stock(self):
        arr = []
        for loc in Locations.objects.all():
            loc_code = loc.code
            name = loc.descr
            stk = ProductTrans.objects.filter(loc=loc,product=self).aggregate(Sum('tran_qty'))['tran_qty__sum'] or 0
            arr.append({
                'loc_code':loc_code,
                'loc_name':name,
                'stock':stk
            })
        if ProductTrans.objects.filter(product=self).aggregate(Sum('tran_qty'))['tran_qty__sum'] is None:
            return 0
        else:
            return ProductTrans.objects.filter(product=self).aggregate(Sum('tran_qty'))['tran_qty__sum']
    def packing(self):
        return ProductPacking.objects.filter(product=self)


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
    type = models.CharField(max_length=10,unique=False,null=False,default="retail")
    server_location = models.TextField(null=True)
    ip_address = models.TextField(null=True)
    db = models.TextField(null=True)
    db_user = models.TextField(null=True)
    db_password = models.TextField(null=True)

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)
    evat_key = models.IntegerField(default=0)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    manager = models.OneToOneField('UserAddOns',on_delete=models.SET_NULL,null=True,blank=True)

    def mana(self):
        man = UserAddOns.objects.filter(pk=self.manager_id)
        obj = {
            "name":None,
            "phone":None,
            'email':None
        }
        if man.count() == 1:
            m = UserAddOns.objects.get(pk=self.manager_id)
            obj['name'] = m.user.username
            obj['phone'] = m.phone
            obj['email'] = m.user.email

        return obj

    def obj(self):
        return {
            'code':self.code,
            'name':self.descr,
            'type':self.type,
            'pk':self.pk
        }
    def evat(self):
        credentials = EvatCredentials.objects.filter(pk=self.evat_key)

        if credentials.count() == 1:
            key = EvatCredentials.objects.get(pk=self.evat_key)
            return key.server_location
        else:
            return "NOT SET"


class TransferHD(models.Model):
    entry_no = models.CharField(max_length=10, unique=True,null=False)
    loc_fr = models.ForeignKey('Locations', on_delete=models.CASCADE,related_name="transfer_location_from")

    loc_to =  models.ForeignKey('Locations', on_delete=models.CASCADE,related_name="transfer_location_to")

    remarks = models.TextField()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="transfer_hd_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    is_posted = models.BooleanField(default=False)

    is_sent = models.BooleanField(default=False)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True,related_name="transfer_sent_by")
    delivery_by = models.CharField(max_length=50,null=True)
    reccieved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True,related_name="transfer_recieved_by")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                     related_name="transfer_approved_by")
    rec_remark = models.TextField(null=True)

    def total_cost(self):
        return TransferTran.objects.filter(parent=self.pk).aggregate(Sum('cost'))['cost__sum']

    def evidence(self):
        from inventory.models import Evidence
        if Evidence.objects.filter(doc_type='TR',entry=self.entry_no).exists():
            evidence = Evidence.objects.filter(doc_type='TR',entry=self.entry_no).last()
            file = evidence.file.url
        else:
            file = 'UNKNOW'

        return file

    def tran_pieces(self):
        return TransferTran.objects.filter(parent=self.pk).aggregate(Sum('tran_qty'))['tran_qty__sum']


    def to(self):
        return Locations.objects.get(pk=self.loc_to)

    def trans(self):
        return TransferTran.objects.filter(parent=self.pk)

    def tran_count(self):
        return TransferTran.objects.filter(parent=self.pk).count()

    def obj(self):

        if self.is_posted:
            status = "POSTED"
        elif self.is_sent:
            status = "SENT"
        else:
            status = "UNKNOWN"

        return {
            "pk":self.pk,
            "from":self.loc_fr.descr,
            "to":self.loc_to.descr,
            "created_by":self.created_by.get_full_name(),
            "entry_no":self.entry_no,
            "next": TransferHD.objects.filter(pk__gt=self.pk).last().pk if TransferHD.objects.filter(pk__gt=self.pk).count() > 0 else 0,
            "previous":TransferHD.objects.filter(pk__lt=self.pk).order_by('-pk').last().pk if TransferHD.objects.filter(pk__lt=self.pk).count() > 0 else 0,
            "remarks":self.remarks,
            "total_cost":format_currency(self.total_cost()),
            "tran_pieces":format_currency(self.tran_pieces()),
            "is_sent":self.is_sent,
            "is_posted":self.is_posted,
            "status":status,
            'evidence':self.evidence(),
            "rec_remark":self.rec_remark

        }



class TransferTran(models.Model):
    parent = models.ForeignKey('TransferHD', on_delete=models.CASCADE)
    line = models.IntegerField()
    product = models.ForeignKey('ProductMaster', on_delete=models.CASCADE)
    packing = models.TextField()
    pack_qty = models.DecimalField(max_digits=65, decimal_places=2,default=0.00)
    tran_qty = models.DecimalField(max_digits=65, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=65, decimal_places=2,default=0.00)
    cost = models.DecimalField(max_digits=65, decimal_places=2,default=0.00)

    def product_name(self):
        return ProductMaster.objects.get(pk=self.product).descr

    def obj(self):
        return {
            "pk":self.pk,
            "product":self.product.obj(),
            "line":self.line,
            "packing":self.packing,
            "pack_qty":self.pack_qty,
            "tran_qty":self.tran_qty,
            "un_cost":self.unit_cost,
            "cost":self.cost
        }


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

    created_on = models.DateTimeField(default=timezone.now)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    app = models.TextField(default='Unknown')

    def transactions(self):
        return TicketTrans.objects.filter(ticket=self).order_by('-pk')


class TicketTrans(models.Model):
    ticket = models.ForeignKey('TicketHd', on_delete=models.CASCADE)
    title = models.TextField(null=True, blank=True)
    tran = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)


class Files(models.Model):
    doc = models.CharField(max_length=3)
    cryp_key = models.CharField(max_length=60)
    media = models.FileField(upload_to=f'static/uploads/%Y%m%d')

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    def file_name(self):
        return os.path.basename(self.media.name)


class AuthToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)


# hold extra user details
class Departments(models.Model):
    name = models.CharField(max_length=255, unique=True)
    name_of_head = models.TextField()
    email_of_head = models.TextField()
    phone_of_head = models.TextField()
    description = models.TextField(null=True)

    def members(self):
        return UserAddOns.objects.filter(department=self)


class UserAddOns(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    about = models.TextField(default='None')
    company = models.TextField()
    position = models.TextField()
    country = models.TextField()
    Address = models.TextField()
    news = models.IntegerField(default=1)
    phone = models.CharField(max_length=14, unique=True)
    app_version = models.ForeignKey('appconfig.VersionHistory', on_delete=models.CASCADE)
    profile_pic = models.FileField(upload_to=f'static/uploads/users/')
    pword_reset = models.IntegerField(default=1)
    api_token = models.TextField(null=True)
    auth_pin = models.CharField(max_length=200)

    department = models.ForeignKey(Departments, on_delete=models.SET_NULL, null=True, blank=True)

    def settings(self):
        return UserSettings.objects.get(user=self.user)

    def dept(self):
        return self.department.name if self.department.name else "NOT ASSIGNED"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    valid = models.IntegerField(1)


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prim_noif = models.TextField(default='email')


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


class OrganizationalUnit(models.Model):
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class UnitMembers(models.Model):
    ou = models.ForeignKey('OrganizationalUnit', on_delete=models.CASCADE)
    name = models.CharField(max_length=60, unique=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class SmsApi(models.Model):
    api_key = models.CharField(max_length=66, unique=True)
    sender_id = models.TextField()
    api_desc = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_default = models.IntegerField(default=0)


# sms queued
class Sms(models.Model):
    api = models.ForeignKey('SmsApi', on_delete=models.CASCADE)
    to = models.CharField(max_length=20, null=False)
    message = models.TextField(null=False)

    last_tried_date = models.TextField()
    last_tried_time = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)


# log sms responses
class SmsResponse(models.Model):
    sms = models.ForeignKey(Sms, on_delete=models.CASCADE)
    resp_code = models.TextField()
    resp_msg = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)


class BulkSms(models.Model):
    api = models.ForeignKey('SmsApi', on_delete=models.CASCADE)
    file = models.FileField(upload_to=f"static/uploads/bsms/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    message = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class BillHeader(models.Model):
    loc_id = models.TextField()
    loc_desc = models.TextField()
    bill_date = models.TextField()
    bill_end_time = models.TextField()
    clrk_code = models.TextField()
    mech_no = models.IntegerField()
    bill_no = models.IntegerField()
    bill_amt = models.DecimalField(max_digits=60, decimal_places=2)
    tax = models.DecimalField(max_digits=60, decimal_places=2)
    paid_amt = models.DecimalField(max_digits=60, decimal_places=2)
    bal_amt = models.DecimalField(max_digits=60, decimal_places=2)
    billRef = models.TextField()
    bill_type = models.CharField(max_length=3)
    pay_mode = models.CharField(max_length=3)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)


class BillTran(models.Model):
    mech_no = models.IntegerField()
    bill_no = models.IntegerField()
    tran_code = models.TextField()
    tran_desc = models.TextField()
    tran_amt = models.DecimalField(max_digits=60, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=60, decimal_places=2)
    billRef = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)


class Department(models.Model):
    name = models.TextField()
    description = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)


class GeoCity(models.Model):
    name = models.CharField(unique=True, max_length=255)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=1)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def timestamp(self):
        return {
            'created_date': self.created_date,
            'created_time': self.created_time,
            'updated_date': self.updated_date,
            'updated_time': self.updated_time,
        }

    def subs(self):
        return GeoCitySub.objects.filter(city=self)


class GeoCitySub(models.Model):
    city = models.ForeignKey(GeoCity, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(unique=True, max_length=255)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=1)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('city', 'name'),)

    def timestamp(self):
        return {
            'created_date': self.created_date,
            'created_time': self.created_time,
            'updated_date': self.updated_date,
            'updated_time': self.updated_time,
        }


class Reminder(models.Model):
    title = models.CharField(max_length=255, null=False)
    message = models.TextField(null=False)
    rem_date = models.DateField(null=False)
    rem_time = models.TimeField(null=False)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=1)  # 1 active, 0 not, 99 done
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    resp_code = models.TextField(default='null')
    resp_message = models.TextField(default='null')

    read_only = models.BooleanField(default=False)


class Contacts(models.Model):
    full_name = models.TextField()
    email = models.CharField(max_length=100, unique=False, null=False)
    phone = models.CharField(max_length=100, unique=False, null=False)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=1)  # 1 active, 0 not, 99 done
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        unique_together = (('owner', 'phone'), ('owner', 'email'))


class EvatCredentials(models.Model):
    server_ip = models.TextField(null=True)
    server_location = models.TextField(null=True)
    company_tin = models.CharField(null=False, unique=False, max_length=20)
    company_name = models.CharField(null=False, unique=True, max_length=100)
    company_security_key = models.CharField(null=False, unique=False, max_length=255)
    inv_req = models.CharField(null=False, unique=True, max_length=255)
    z_rez = models.CharField(null=False, unique=True, max_length=255)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=1)  # 1 active, 0 not, 99 done
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def stat(self):
        if self.status == 1:
            return 'ACTIVE'
        elif self.status == 0:
            return 'INACTIVE'
        else:
            return 'UNKNOWN'


class Log500(models.Model):

    path = models.TextField()
    what = models.TextField()
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)


class DocApprovals(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    doc_type = models.CharField(max_length=200)

    class Meta:
        unique_together = (('user', 'doc_type'),)