import hashlib

from django.contrib.auth.models import User
from django.db import models
import os
from django.db import models
from django.utils import timezone
from cryptography.fernet import Fernet


class Files(models.Model):
    file = models.FileField(upload_to='static/uploads/%Y/%m/%d/')

    size = models.TextField()
    type = models.TextField()
    enc = models.CharField(max_length=60, unique=True)

    status = models.IntegerField(default=1)
    date_crated = models.DateField(auto_now_add=True)
    time_created = models.TimeField(auto_now_add=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def time(self):
        return f"{self.date_crated} {self.time_created}"

    def filename(self):
        return os.path.basename(self.file.name)

    def delete(self, *args, **kwargs):
        # Remove the file from the file system.
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        # Call the parent class's delete() method to delete the object from the database.
        super(Files, self).delete(*args, **kwargs)


class Documents(models.Model):
    doc = models.CharField(max_length=3)
    entry_no = models.TextField()
    file = models.FileField(upload_to='static/uploads/%Y/%m/%d/')
