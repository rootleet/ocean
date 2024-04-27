from django.conf import settings
from django.db import models
from django.db.models import Sum

from admin_panel.models import GeoCity, GeoCitySub


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

    approve = models.IntegerField(default=0)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def trans(self):
        return {
            'count': StockCountTrans.objects.filter(stock_count_hd=self.pk).count(),
            'trans': StockCountTrans.objects.filter(stock_count_hd=self.pk),
            'summary': {
                'total_frozen':
                    StockCountTrans.objects.filter(stock_count_hd=self.pk).aggregate(total_amount=Sum('froze_qty'))[
                        'total_amount'],
                'total_counted':
                    StockCountTrans.objects.filter(stock_count_hd=self.pk).aggregate(total_amount=Sum('counted_qty'))[
                        'total_amount'],
                'qty_difference':
                    StockCountTrans.objects.filter(stock_count_hd=self.pk).aggregate(total_amount=Sum('diff_qty'))[
                        'total_amount'],
                'value_frozen':
                    StockCountTrans.objects.filter(stock_count_hd=self.pk).aggregate(total_amount=Sum('froze_val'))[
                        'total_amount'],
                'value_counted':
                    StockCountTrans.objects.filter(stock_count_hd=self.pk).aggregate(total_amount=Sum('counted_val'))[
                        'total_amount'],
                'value_difference':
                    StockCountTrans.objects.filter(stock_count_hd=self.pk).aggregate(total_amount=Sum('diff_val'))[
                        'total_amount']
            }
        }

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

    froze_qty = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)
    counted_qty = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)
    diff_qty = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)

    froze_val = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)
    counted_val = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)
    diff_val = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)

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
    status = models.IntegerField(default=1)  # { 1: Pending, 2: Counted, 0: Deleted }
    approve = models.IntegerField(default=0)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def posted(self):
        ret = 0
        if StockCountHD.objects.filter(frozen=self).count() == 1:
            ret = 1

        return ret

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
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)


class SalesCustomers(models.Model):
    sector_of_company = models.TextField(blank=True)
    type_of_client = models.TextField()
    company = models.CharField(max_length=225, unique=True)
    region = models.ForeignKey(GeoCity, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(GeoCitySub, on_delete=models.SET_NULL, null=True, blank=True)
    mobile = models.CharField(max_length=225, unique=True)
    email = models.CharField(max_length=225, unique=True)
    fax = models.TextField(blank=True)
    address = models.TextField()

    first_name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    position = models.TextField(default='none')
    note = models.TextField(null=True, blank=True)
    name = models.TextField()

    url = models.CharField(max_length=225, unique=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def trans(self):
        return SalesCustomerTransactions.objects.filter(customer=self.pk).order_by('-pk')

    def uni(self):
        return self.company.replace(' ', '-').lower()

    def deals(self):
        return SalesDeals.objects.filter(customer=self.pk).order_by('-pk')

    def delete(self, *args, **kwargs):
        related_objects = self.salescustomertransactions_set.all()  # replace 'yourmodel' with the lowercased model name that has the 'customer' field
        for obj in related_objects:
            obj.customer = self.name
            obj.save()
        super().delete(*args, **kwargs)


class SalesCustomerTransactions(models.Model):
    customer = models.ForeignKey(SalesCustomers, on_delete=models.SET_NULL, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.TextField()
    details = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    def date(self):
        return f"{self.created_date} {self.created_time}"


class SalesDeals(models.Model):
    customer = models.ForeignKey(SalesCustomers, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    pur_rep_name = models.TextField()
    pur_rep_email = models.TextField()
    pur_rep_phone = models.TextField()

    asset = models.TextField()
    model = models.TextField()
    stock_type = models.IntegerField(default=0)

    requirement = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)

    status = models.IntegerField(default=0)  # 0 open, 1 closed, 3 invalid

    finale = models.IntegerField(default=0)  # 0 failed, 1 success

    def transactions(self):
        return DealTransactions.objects.filter(deal=self.pk).order_by('-pk')


class DealTransactions(models.Model):
    deal = models.ForeignKey(SalesDeals, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.TextField()
    details = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)


class SalesAssetsGroup(models.Model):
    name = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def obj(self):
        return {
            'name': self.name,
            'created_date': self.created_date,
            'created_time': self.created_time,
            'updated_date': self.created_date,
            'owner':self.owner.get_fullname()

        }

