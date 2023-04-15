from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def has_perm(user, perm):
    return user.has_perm(perm)