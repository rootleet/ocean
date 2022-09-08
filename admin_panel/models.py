from django.contrib.auth.models import User
from django.db import models
from community.models import questions, QuestionTags
from blog.models import Providers


# Create your models here.

class LoggedIssue(models.Model):
    issue = models.CharField(unique=True, max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def log_count(self):  # log count
        return LoggedIssue.objects.filter(issue=self.issue).count()

    def domain(self):  # tags
        # from community.models import QuestionTags
        quest =  questions.objects.get(uni=self.issue)
        return quest.domain

    def owner(self):  # owner name
        owner_detail = questions.objects.get(uni=self.issue)
        owner_id = owner_detail.owner
        return User.objects.get(pk=owner_id)

    def title(self):
        return questions.objects.get(uni=self.issue).title

    def date_reported(self):
        return questions.objects.get(uni=self.issue).created_at

    def stat(self):
        if self.status == 0:
            return "PENDING"
        elif self.status == 1:
            return "TO SEND"
        else:
            return f"UNKNOWN ({self.status})"


class LoggedIssueTransaction(models.Model):
    issue = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(default=0)
    title = models.CharField(max_length=100)
    body = models.TextField()

    def owner(self):
        return User.objects.get(pk=self.created_by)


class PendingEscalations(models.Model):
    provider = models.CharField(max_length=5)
    issue = models.CharField(unique=True, max_length=100)

    def quest(self):
        return questions.objects.get(uni=self.issue)



class TaskHD(models.Model): ## task model
    entry_uni = models.TextField()
    type = models.TextField()
    ref = models.TextField()
    owner = models.IntegerField(default=0)
    title = models.TextField()
    description = models.TextField()
    added_on = models.DateTimeField(auto_now=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    domain = models.ForeignKey('blog.Providers',on_delete=models.CASCADE)
    def owner_name(self):
        return User.objects.get(pk=self.owner).username

    def question(self):
        return questions.object.get(uni=self.ref)



# task transactions
class TaskTrans(models.Model):
    entry_uni = models.TextField()
    tran_title = models.TextField()
    tran_descr = models.TextField()
    created_on = models.DateTimeField(auto_now=True)
    owner = models.IntegerField(default=0)
    def owner_name(self):
        return User.objects.get(pk=self.owner)
