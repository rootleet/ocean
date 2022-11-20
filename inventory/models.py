from django.conf import settings
from django.db import models
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

    approved_by = models.TextField()
    approved_date = models.DateField()
    approved_time = models.TimeField()

    def trans(self):
        return PoTran.objects.get(entry_no=self.pk)

    def tran_count(self):
        return PoTran.objects.filter(entry_no=self.pk).count()


# purchase trans
class PoTran(models.Model):
    entry_no = models.ForeignKey('PoHd', on_delete=models.CASCADE)
    line = models.IntegerField()
    product = models.ForeignKey('admin_panel.ProductMaster', on_delete=models.CASCADE)
    packing = models.TextField()
    qty = models.DecimalField(max_digits=65, decimal_places=2)
    total_qty = models.IntegerField()
    un_cost = models.DecimalField(max_digits=60, decimal_places=2)
    tot_cost = models.DecimalField(max_digits=60, decimal_places=2)
