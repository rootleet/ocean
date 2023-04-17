from django import template
register = template.Library()


@register.simple_tag
def custom_tags (user, perm):
    return user.has_perm(perm)
