import os

from django import template

from admin_panel.models import UserAddOns
from ocean import settings
from ocean.settings import BASE_DIR

register = template.Library()


@register.filter(name='has_permission')
def has_permission(user, permission_name):
    if user.user_permissions.filter(codename=permission_name).exists():
        return True
    else:
        return False


@register.filter(name='my_profile_picture')
def my_dp(user):
    if UserAddOns.objects.filter(user=user).exists():
        ad_on = UserAddOns.objects.get(user=user)

        # Check if a file is associated with the profile_pic field
        if ad_on.profile_pic and ad_on.profile_pic.name:
            file = ad_on.profile_pic.path
            if os.path.isfile(file):
                rel_path = os.path.relpath(file, settings.STATIC_ROOT)
                return rel_path
        return '/static/assets/img/users/user.png'

    else:
        return '/static/assets/img/users/user.png'
