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
    id = models.IntegerField(primary_key=True)
    description = models.TextField()
    status = models.IntegerField(default=1)
    created_at = models.TextField()
    updated_at = models.TextField()
    owner = models.CharField(max_length=200, default='anton')

    def __str__(self):
        return str(self.description)


class userAccounts(models.Model):
    username = models.TextField(max_length=1000)
    token = models.TextField(max_length=1000)
    meta_words = models.TextField(max_length=1000)

    def __str__(self):
        return str(self.token)


class ArticleView(models.Model):
    article = models.TextField()
    user = models.IntegerField(default=0)


class Notofication(models.Model):
    sent_from = models.IntegerField(default=0)
    sent_to = models.IntegerField(default=0)
    title = models.TextField()
    message = models.TextField()
    sent_on = models.DateTimeField(auto_now_add=True)
    read = models.IntegerField(default=0)


class Providers(models.Model):
    provider_code = models.CharField(max_length=3)
    descr = models.TextField()
    mobile = models.TextField()
    email = models.TextField()
