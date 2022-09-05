import datetime

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from admin_panel.models import * 
# todo import admin panel models

# Create your models here.
from django.db.models import Count


class tags(models.Model):
    tag_code = models.CharField(max_length=3)
    tag_dec = models.TextField()
    provider = models.IntegerField(default=0)


class QuestionTags(models.Model):
    question = models.TextField()
    tag = models.TextField()

    def __str__(self):
        return self.tag


# questions model
class questions(models.Model):
    uni = models.CharField(unique=True, max_length=100)
    title = models.TextField()
    body = models.TextField()
    owner = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    domain = models.TextField(default='OTH')

    def quest_logged(self):
        from admin_panel.models import LoggedIssue
        return LoggedIssue.objects.filter(issue=self.uni).count()

    def owner_name(self):
        return User.objects.get(pk=self.owner)

    def provider(self):
        from blog.models import Providers
        tag_detail = tags.objects.get(tag_code=self.domain)
        return "Hello World Love Is Wicked"

    def readers(self):
        return QuestionViews.objects.filter(question=self.uni).count()

    def task(self):
        return TaskHD.objects.filter(entry_uni=self.uni).count()


# answer
class answers(models.Model):
    user = models.IntegerField(default=0)
    question = models.TextField()
    ans = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ans

    def owner(self):
        return User.objects.get(pk=self.user)

    def time_ago(self):
        import datetime

        # datetime(year, month, day, hour, minute, second)
        comment_year = self.comment_date.year

        a = datetime.datetime(self.comment_date.year,
                              self.comment_date.month,
                              self.comment_date.day,
                              self.comment_date.hour,
                              self.comment_date.minute,
                              self.comment_date.second)
        b = datetime.datetime.now()

        # returns a timedelta object
        c = b - a
        print('Difference: ', c)

        minutes = c.total_seconds() / 60
        print('Total difference in minutes: ', minutes)

        # returns the difference of the time of the day
        minutes = c.seconds / 60

        return f"{int(minutes)}"


class QuestionViews(models.Model):
    question = models.TextField()
    user = models.IntegerField(default=0)

