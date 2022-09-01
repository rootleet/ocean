from datetime import datetime

from django.db import models


# Create your models here.
class Videos(models.Model):
    key = models.TextField()
    title = models.TextField()
    descr = models.TextField()
    file = models.FileField(upload_to=f'static/general/videos/')

