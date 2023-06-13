from decimal import Decimal
from jsonfield import JSONField
from django.conf import settings
from django.db import models
from django.db.models import Sum

from admin_panel.models import SuppMaster, Locations, ProductMaster


# price master
class PriceCenter(models.Model):
    product = models.ForeignKey('admin_panel.ProductMaster', on_delete=models.CASCADE)
    price_type = models.CharField(max_length=1)
    price = models.DecimalField(max_digits=60, decimal_places=2)


# purchasing hd
class PoHd(models.Model):
    entry_no = models.TextField()
    loc = models.ForeignKey('admin_panel.Locations', on_delete=models.CASCADE)
    supplier = models.ForeignKey('admin_panel.SuppMaster', on_delete=models.CASCADE)
    remark = models.TextField()

    taxable = models.IntegerField(default=1)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    open = models.IntegerField(default=1)

    def trans(self):
        return PoTran.objects.get(entry_no=self.pk)

    def tran_count(self):
        return PoTran.objects.filter(entry_no=self.pk).count()

    def total_amt(self):
        if PoTran.objects.filter(entry_no=self).aggregate(Sum('tot_cost'))['tot_cost__sum'] is None:
            return 0
        else:
            return PoTran.objects.filter(entry_no=self).aggregate(Sum('tot_cost'))['tot_cost__sum']

    def tax_amt(self):

        tax_details = {
            'tax_nhis': 0.00,
            'tax_gfund': 0.00,
            'tax_covid': 0.00,
            'tax_vat': 0.00,
            'tax_amt': 0.00
        }

        if self.taxable == 1:
            taxable_amt = self.total_amt()
            tax_details['tax_covid'] = round(Decimal(taxable_amt) * Decimal(0.001), 2)
            tax_details['tax_nhis'] = round(Decimal(taxable_amt) * Decimal(0.025), 2)
            tax_details['tax_gfund'] = round(Decimal(taxable_amt) * Decimal(0.025), 2)

            levies = tax_details['tax_covid'] + tax_details['tax_nhis'] + tax_details['tax_gfund']
            new_tot_amt = taxable_amt + levies

            tax_details['tax_vat'] = round(Decimal(new_tot_amt) * Decimal(0.125), 2)
            tax_details['tax_amt'] = round(levies + tax_details['tax_vat'], 2)

        return tax_details

    def new_amt(self):
        return Decimal(self.total_amt()) + Decimal(self.tax_amt()['tax_amt'])


# purchase trans
class PoTran(models.Model):
    entry_no = models.ForeignKey('PoHd', on_delete=models.CASCADE)
    line = models.IntegerField()
    product = models.ForeignKey('admin_panel.ProductMaster', on_delete=models.CASCADE)
    packing = models.ForeignKey('admin_panel.ProductPacking', on_delete=models.CASCADE)
    pack_qty = models.DecimalField(max_digits=65, decimal_places=2)
    qty = models.DecimalField(max_digits=65, decimal_places=2)
    total_qty = models.IntegerField()
    un_cost = models.DecimalField(max_digits=60, decimal_places=2)
    tot_cost = models.DecimalField(max_digits=60, decimal_places=2)


# GRN
class GrnHd(models.Model):
    type = models.TextField()
    ref = models.TextField()
    entry_no = models.TextField()
    loc = models.ForeignKey('admin_panel.Locations', on_delete=models.CASCADE)
    supplier = models.ForeignKey('admin_panel.SuppMaster', on_delete=models.CASCADE)
    remark = models.TextField()

    taxable = models.IntegerField(default=1)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    # edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def trans(self):
        return GrnTran.objects.get(entry_no=self.pk)

    def tran_count(self):
        return GrnTran.objects.filter(entry_no=self.pk).count()


# GRN trans
class GrnTran(models.Model):
    entry_no = models.ForeignKey('GrnHd', on_delete=models.CASCADE)
    line = models.IntegerField()
    product = models.ForeignKey('admin_panel.ProductMaster', on_delete=models.CASCADE)
    packing = models.ForeignKey('admin_panel.ProductPacking', on_delete=models.CASCADE)
    pack_qty = models.TextField()
    qty = models.DecimalField(max_digits=65, decimal_places=2)
    total_qty = models.IntegerField()
    un_cost = models.DecimalField(max_digits=60, decimal_places=2)
    tot_cost = models.DecimalField(max_digits=60, decimal_places=2)


# document approvals
class DocAppr(models.Model):
    entry_no = models.TextField()
    doc_type = models.TextField()

    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    approved_on = models.DateTimeField(auto_now_add=True)


class AssetGroup(models.Model):
    descr = models.TextField()

    created_on = models.DateTimeField(auto_now_add=True)


class Assets(models.Model):
    group = models.ForeignKey('inventory.AssetGroup', on_delete=models.CASCADE)
    brand = models.TextField()
    type = models.IntegerField(default=0)

    descr = models.TextField()
    sku = models.CharField(max_length=60, unique=True)
    model = models.TextField()
    manufacturer = models.TextField()

    storage = models.TextField()
    memory = models.TextField()
    processor = models.TextField()

    details = models.TextField()
    image = models.FileField(upload_to=f'static/general/img/products/', default='static/general/img/products/asset.png')
    tags = models.TextField(default='NULL')

    created_on = models.DateTimeField(auto_now_add=True)


class WorkStation(models.Model):
    sys_uni = models.ForeignKey('inventory.Assets', on_delete=models.CASCADE, related_name='related_sys_uni')
    monitor = models.ForeignKey('inventory.Assets', on_delete=models.CASCADE, related_name='related_moni')
    keyboard = models.ForeignKey('inventory.Assets', on_delete=models.CASCADE, related_name='related_kb')
    mouse = models.ForeignKey('inventory.Assets', on_delete=models.CASCADE, related_name='related_mouse')
    printer = models.TextField(default='NULL')
    ups = models.TextField(default='NULL')

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)
    owner = models.ForeignKey('admin_panel.UnitMembers', on_delete=models.CASCADE)


class Computer(models.Model):
    group = models.ForeignKey('ComputerGroup', on_delete=models.SET_NULL, null=True)
    ram_type = models.CharField(max_length=255)
    ram_size = models.PositiveIntegerField()
    cpu = models.CharField(max_length=255)
    storage_type = models.CharField(max_length=255)
    storage_size = models.CharField(max_length=255)
    used_storage = models.CharField(max_length=255)
    remaining_storage = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=255,unique=True)
    manufacturer = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    os = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    printer = models.TextField()
    logged_on_user = models.CharField(max_length=255)
    computer_name = models.CharField(max_length=255)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def __str__(self):
        return self.mac_address


class ComputerMoreInfo(models.Model):
    computer = models.ForeignKey('Computer', on_delete=models.CASCADE)
    department = models.ForeignKey('admin_panel.Department', on_delete=models.SET_NULL,null=True)

    monitor = models.TextField()

    keyword = models.TextField()
    mouse = models.TextField()

    ups = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)


class ComputerGroup(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

