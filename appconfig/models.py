import pathlib

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from community.models import questions, QuestionTags
from blog.models import Providers
from django.db.models import Sum


class VersionHistory(models.Model):
    version = models.TextField()
    descr = models.TextField()
