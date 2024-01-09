from django.contrib.auth.models import User
from django.db import models
from django.db.models import ForeignKey


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
    name = models.CharField(unique=True, max_length=266)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def items(self):
        return BoltItems.objects.filter(group=self)


class BoltItems(models.Model):
    group = models.ForeignKey(BoltGroups, on_delete=models.CASCADE)
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


class ProductSupplier(models.Model):
    code = models.CharField(unique=True, max_length=60)
    name = models.CharField(unique=True, max_length=60)
    person = models.TextField()
    phone = models.TextField()
    email = models.TextField()
    city = models.TextField()
    country = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)


class ProductGroup(models.Model):
    code = models.CharField(unique=True, max_length=10, null=False, blank=False)
    name = models.CharField(unique=True, max_length=60)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def subgroups(self):
        return ProductSubGroup.objects.filter(group=self)


class ProductSubGroup(models.Model):
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE)
    code = models.CharField(unique=False, max_length=10)
    name = models.CharField(unique=False, max_length=60)
    created_on = models.DateTimeField(auto_now_add=True)

    def products(self):
        return Products.objects.filter(subgroup=self)

    class Meta:
        unique_together = (('group', 'code'),)


class Products(models.Model):
    subgroup = models.ForeignKey(ProductSubGroup, on_delete=models.CASCADE)
    code = models.CharField(unique=True, max_length=60)
    barcode = models.CharField(unique=True, max_length=100, null=False, blank=False)
    name = models.TextField(null=False)
    price = models.DecimalField(decimal_places=2, max_digits=60)

    def is_on_bolt(self):
        barcode = self.barcode.strip()
        if BoltItems.objects.filter(barcode=barcode).exists():
            return True
        else:
            return False


class Stock(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, null=False, blank=False)
    quantity = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)

    class Meta:
        unique_together = (('product', 'location'),)


class RecipeGroup(models.Model):
    name = models.CharField(null=False, blank=False, max_length=60)
    is_open = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def products(self):
        return RecipeProduct.objects.filter(group=self)

    class Meta:
        unique_together = (('name', 'owner'),)


class RecipeProduct(models.Model):
    group = ForeignKey(RecipeGroup, on_delete=models.CASCADE)
    name = models.CharField(null=False, blank=False, max_length=60)
    barcode = models.TextField(null=False, blank=False)
    si_unit = models.TextField(null=False, blank=False)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('name', 'owner', 'group'),)

    def recipe_items(self):
        return Recipe.objects.filter(product=self).count()

    def recipe(self):
        return Recipe.objects.filter(product=self)


class Recipe(models.Model):
    product = models.ForeignKey(RecipeProduct, on_delete=models.CASCADE)
    name = models.TextField(null=False, blank=False)
    quantity = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    si_unit = models.TextField(null=False, blank=False)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('name', 'owner', 'product'),)
