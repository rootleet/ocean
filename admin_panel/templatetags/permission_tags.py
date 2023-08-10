from django import template

register = template.Library()


@register.filter(name='has_permission')
def has_permission(user, permission_name):
    if user.user_permissions.filter(codename=permission_name).exists():
        return True
    else:
        return False
