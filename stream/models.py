import os
from datetime import datetime

from django.db import models


# Create your models here.
class Videos(models.Model):
    key = models.TextField()
    title = models.TextField()
    descr = models.TextField()
    file = models.FileField(upload_to=f'static/uploads/videos/')

    def thumbnail(self):
        file_path = f'/static/general/videos/{self.key}.jpg'
        if os.path.exists(file_path):
            return file_path
        else:
            return '/static/general/videos/img.png'

