from django.conf import settings
from django.db import models
from django.db.models import Sum


# follow-ups
class FollowUp(models.Model):
    carno = models.CharField(max_length=10)
    title = models.TextField()
    message = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


# stock hd
class StockCountHD(models.Model):
    frozen = models.OneToOneField('StockFreezeHd', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    comment = models.TextField()
    status = models.IntegerField(default=1)  # 1, active, #2 closed

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def entry_no(self):
        return f"STK{self.pk}{self.frozen.loc_id}"

    def op(self):
        if self.status == 1:
            return {
                'class': 'bg-success', 'text': 'OPEN'
            }
        else:
            return {
                'class': 'bg-secondary', 'text': 'CLOSED'
            }

    def qty(self):
        return StockCountTrans.objects.filter(stock_count_hd=self).aggregate(total=Sum('quantity'))['total']

    def value(self):
        return StockCountTrans.objects.filter(stock_count_hd=self).aggregate(total=Sum('value'))['total']

    def next(self):
        if StockCountHD.objects.filter(pk__gt=self.pk).count() > 0:
            pk = StockCountHD.objects.filter(pk__gt=self.pk).first().pk
            valid = 'Y'
        else:
            valid = 'N'
            pk = False
        return {
            'valid': valid, 'pk': pk, 'counted': StockCountHD.objects.filter(pk__gt=self.pk).count()
        }

    def prev(self):
        if StockCountHD.objects.filter(pk__lt=self.pk).count() > 0:
            pk = StockCountHD.objects.filter(pk__lt=self.pk).last().pk
            valid = 'Y'
        else:
            valid = 'N'
            pk = False
        return {
            'valid': valid, 'pk': pk, 'counted': StockCountHD.objects.filter(pk__lt=self.pk).count()
        }



class StockCountTrans(models.Model):
    stock_count_hd = models.ForeignKey(StockCountHD, on_delete=models.CASCADE)
    item_ref = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)
    name = models.TextField()

    froze_qty = models.DecimalField(max_digits=10, decimal_places=3,default=0.00)
    counted_qty = models.DecimalField(max_digits=10, decimal_places=3,default=0.00)
    diff_qty = models.DecimalField(max_digits=10, decimal_places=3,default=0.00)

    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)
    sell_price = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)
    value = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)
    comment = models.TextField(default='null')
    issue = models.TextField(default='null')

    owner = models.TextField(default='Anonymous')



class StockFreezeHd(models.Model):
    loc_id = models.CharField(max_length=3, blank=False, null=False)
    ref = models.TextField(blank=False, null=False)
    remarks = models.TextField(blank=False, null=False)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)  # { 1: Pending, 2: Counted, 0: Invalid }

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def trans(self):
        return {
            'count': StockFreezeTrans.objects.filter(entry_id=self.pk).count(),
            'trans': StockFreezeTrans.objects.filter(entry_id=self.pk)
        }

    def trans_only(self):
        return StockFreezeTrans.objects.filter(entry_id=self.pk)
    def next(self):
        if StockFreezeHd.objects.filter(pk__gt=self.pk).count() > 0:
            pk = StockFreezeHd.objects.filter(pk__gt=self.pk).first().pk
            valid = 'Y'
        else:
            valid = 'N'
            pk = False
        return {
            'valid': valid, 'pk': pk, 'counted': StockFreezeHd.objects.filter(pk__gt=self.pk).count()
        }

    def prev(self):
        if StockFreezeHd.objects.filter(pk__lt=self.pk).count() > 0:
            pk = StockFreezeHd.objects.filter(pk__lt=self.pk).last().pk
            valid = 'Y'
        else:
            valid = 'N'
            pk = False
        return {
            'valid': valid, 'pk': pk, 'counted': StockFreezeHd.objects.filter(pk__lt=self.pk).count()
        }

    def ent(self):
        return f"FR{self.loc_id}{self.pk}"


class StockFreezeTrans(models.Model):
    entry = models.ForeignKey('StockFreezeHd', on_delete=models.CASCADE)
    item_ref = models.CharField(max_length=100, blank=False, null=False)
    barcode = models.CharField(max_length=100, blank=False, null=False)
    name = models.TextField(blank=False, null=False)
    qty = models.DecimalField(max_digits=10, decimal_places=3)
