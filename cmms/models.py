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
    
    loc = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    remark = models.TextField()
    status = models.IntegerField(default=1) #1, active, #2 closed


    def __str__(self):
        return self.code
    def entry_no(self):
        return f"STK{self.pk}{self.loc}"
    def op(self):
        if self.status == 1:
            return  {
                'class':'bg-success','text':'OPEN'
            }
        else:
            return  {
                'class':'bg-secondary','text':'CLOSED'
            }
    def qty(self):
        return StockCountTrans.objects.filter(stock_count_hd=self).aggregate(total=Sum('quantity'))['total']
    def value(self):
        return StockCountTrans.objects.filter(stock_count_hd=self).aggregate(total=Sum('value'))['total']

    

class StockCountTrans(models.Model):
    stock_count_hd = models.ForeignKey(StockCountHD, on_delete=models.CASCADE)
    item_ref = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)
    name = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    sell_price = models.DecimalField(max_digits=10, decimal_places=3)
    value = models.DecimalField(max_digits=10, decimal_places=3)
    
    owner = models.TextField(default='Ananymouse')


    def __str__(self):
        return f"{self.stock_count_hd.code} - {self.item}"
