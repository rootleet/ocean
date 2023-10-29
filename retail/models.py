from django.db import models


# CLERKS
class Clerk(models.Model):
    location = models.ForeignKey('admin_panel.Locations', on_delete=models.CASCADE)
    first_name = models.TextField()
    last_name = models.TextField()
    phone = models.CharField(max_length=10, unique=True, null=False)
    code = models.CharField(max_length=4, unique=True, null=False)
    pword = models.TextField()
    img = models.ImageField(upload_to='static/general/clerks/', default='static/general/img/users/default.png')

    flag_dwn = models.IntegerField(default=1)
    flag_disable = models.IntegerField(default=0)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def name(self):
        return f"{self.first_name} {self.last_name}"


class BoltGroups(models.Model):
    name = models.CharField(unique=True,max_length=266)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)


class BoltItems(models.Model):
    group = models.ForeignKey(BoltGroups,on_delete=models.CASCADE)
    barcode = models.CharField(unique=True, max_length=100, null=False, blank=False)
    item_des = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    price_diff = models.IntegerField(default=0)
    inv_price = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)

    stock_nia = models.IntegerField(null=False, blank=False)
    stock_spintex = models.IntegerField(null=False, blank=False)
    stock_osu = models.IntegerField(null=False, blank=False)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
