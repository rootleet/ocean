from django.contrib.auth.models import User
from django.db import models


def get_username_on_delete(user):
    return user.username if user else None


# Create your models here.
class Logs(models.Model):
    customer = models.TextField(null=False,blank=False)
    flag = models.TextField()
    phone = models.TextField()
    subject = models.TextField()
    description = models.TextField()
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=get_username_on_delete)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
