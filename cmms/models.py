from django.conf import settings
from django.db import models


# follow-ups
class FollowUp(models.Model):
    carno = models.CharField(max_length=10)
    title = models.TextField()
    message = models.TextField()

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now=True)
    status = models.IntegerField(default=1)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
