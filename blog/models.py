from django.db import models
from PIL import Image



# Create your models here.
class articles(models.Model):
    uni = models.CharField(max_length=200)
    owner = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    article = models.TextField()
    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=200)
    intro = models.TextField(default='none')
    meta = models.CharField(max_length=200, default='none')
    image = models.ImageField(upload_to='static/blog/asssets/article/', default='1.jpg')

    def __str__(self):
        return self.title + ' - ' + self.article



class article_meta(models.Model):

    description = models.TextField()
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.CharField(max_length=200, default='anton')

    def __str__(self):
        return self.description + ' - ' + self.status
